import os
from datetime import UTC, date as date_type, datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from pymongo import MongoClient

load_dotenv()

app = FastAPI(title="CarryOn - Golf Shot Tracker")

# MongoDB connection (lazy initialization for serverless)
_client: Optional[MongoClient] = None


def get_shots_collection():
    """Get MongoDB collection, initializing connection if needed."""
    global _client
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    if _client is None:
        _client = MongoClient(uri)
    return _client.carryon.shots


def get_ideas_collection():
    """Get MongoDB ideas collection, initializing connection if needed."""
    global _client
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    if _client is None:
        _client = MongoClient(uri)
    return _client.carryon.ideas


def verify_pin(x_pin: str = Header(None)):
    """Verify PIN from request header."""
    expected_pin = os.getenv("APP_PIN")
    if not expected_pin:
        return  # No PIN configured, allow all
    if x_pin != expected_pin:
        raise HTTPException(status_code=401, detail="Invalid PIN")


class ShotCreate(BaseModel):
    club: str
    distance: Optional[int] = None
    fail: bool = False
    date: date_type = Field(default_factory=date_type.today)


class Shot(BaseModel):
    id: str
    club: str
    distance: Optional[int] = None
    fail: bool = False


class IdeaCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000)


@app.get("/", response_class=HTMLResponse)
async def serve_form():
    """Serve the golf shot entry form."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "public", "index.html")

    # For Vercel deployment, the file might be in a different location
    if not os.path.exists(html_path):
        html_path = os.path.join(os.path.dirname(__file__), "public", "index.html")

    if not os.path.exists(html_path):
        # Return inline HTML as fallback
        return get_inline_html()

    with open(html_path, "r") as f:
        return f.read()


@app.post("/api/verify-pin")
async def verify_pin_endpoint(x_pin: str = Header(None)):
    """Verify if the provided PIN is correct."""
    expected_pin = os.getenv("APP_PIN")
    if not expected_pin:
        return {"valid": True, "message": "No PIN required"}
    if x_pin == expected_pin:
        return {"valid": True, "message": "PIN verified"}
    raise HTTPException(status_code=401, detail="Invalid PIN")


@app.post("/api/shots")
async def create_shot(shot: ShotCreate, x_pin: str = Header(None)):
    """Record a new golf shot."""
    verify_pin(x_pin)

    shots_collection = get_shots_collection()
    if shots_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    if not shot.fail and shot.distance is None:
        raise HTTPException(status_code=400, detail="Distance required when not a fail")

    doc = {
        "club": shot.club,
        "distance": shot.distance if not shot.fail else None,
        "fail": shot.fail,
        "date": shot.date.isoformat(),
        "created_at": datetime.now(UTC).isoformat(),
    }

    result = shots_collection.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "message": "Shot recorded successfully",
        "shot": {
            "club": shot.club,
            "distance": shot.distance,
            "fail": shot.fail,
            "date": shot.date.isoformat(),
        }
    }


@app.get("/api/shots")
async def list_shots(limit: int = 20, x_pin: str = Header(None)):
    """List recent shots."""
    verify_pin(x_pin)
    shots_collection = get_shots_collection()
    if shots_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    shots = []
    cursor = shots_collection.find().sort("created_at", -1).limit(limit)

    for doc in cursor:
        shots.append({
            "id": str(doc["_id"]),
            "club": doc["club"],
            "distance": doc.get("distance"),
            "fail": doc.get("fail", False),
            "date": doc["date"],
            "created_at": doc["created_at"],
        })

    return {"shots": shots, "count": len(shots)}


@app.post("/api/ideas")
async def create_idea(idea: IdeaCreate, x_pin: str = Header(None)):
    """Submit a new idea."""
    verify_pin(x_pin)

    ideas_collection = get_ideas_collection()
    if ideas_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    created_at = datetime.now(UTC).isoformat()
    doc = {
        "description": idea.description,
        "created_at": created_at,
    }

    result = ideas_collection.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "message": "Idea submitted successfully",
        "idea": {
            "description": idea.description,
            "created_at": created_at,
        }
    }


@app.get("/api/ideas")
async def list_ideas(limit: int = 50, x_pin: str = Header(None)):
    """List submitted ideas."""
    verify_pin(x_pin)

    ideas_collection = get_ideas_collection()
    if ideas_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    ideas = []
    cursor = ideas_collection.find().sort("created_at", -1).limit(limit)

    for doc in cursor:
        ideas.append({
            "id": str(doc["_id"]),
            "description": doc["description"],
            "created_at": doc["created_at"],
        })

    return {"ideas": ideas, "count": len(ideas)}


def get_inline_html() -> str:
    """Return inline HTML for the form (fallback for Vercel)."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CarryOn - Golf Shot Tracker</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 400px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { text-align: center; color: #2d5a27; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input, select { width: 100%; padding: 14px; font-size: 16px; border: 2px solid #ddd; border-radius: 8px; background: white; }
        input:focus, select:focus { outline: none; border-color: #2d5a27; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; }
        .checkbox-group input { width: auto; transform: scale(1.5); }
        button { width: 100%; padding: 16px; font-size: 18px; font-weight: 600; color: white; background: #2d5a27; border: none; border-radius: 8px; cursor: pointer; margin-top: 10px; }
        button:active { background: #1e3d1a; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .message { padding: 12px; border-radius: 8px; margin-top: 20px; text-align: center; }
        .message.success { background: #d4edda; color: #155724; }
        .message.error { background: #f8d7da; color: #721c24; }
        .recent-shots { margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; }
        .shot-item { background: white; padding: 12px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .shot-club { font-weight: 600; color: #2d5a27; }
        .shot-distance { color: #666; }
        .shot-fail { color: #dc3545; font-weight: 600; }
        #pinScreen { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: #f5f5f5; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; z-index: 100; }
        #pinScreen.hidden { display: none; }
        #pinForm { width: 100%; max-width: 300px; }
    </style>
</head>
<body>
    <div id="pinScreen">
        <h1>CarryOn</h1>
        <form id="pinForm">
            <div class="form-group">
                <label for="pin">Enter PIN</label>
                <input type="password" id="pin" name="pin" inputmode="numeric" pattern="[0-9]*" placeholder="PIN" required>
            </div>
            <button type="submit">Unlock</button>
            <div id="pinMessage"></div>
        </form>
    </div>
    <h1>CarryOn</h1>
    <form id="shotForm">
        <div class="form-group"><label for="date">Date</label><input type="date" id="date" name="date" required></div>
        <div class="form-group"><label for="club">Club</label>
            <select id="club" name="club" required>
                <option value="">Select club...</option>
                <option value="d">Driver</option><option value="3w">3 Wood</option><option value="5w">5 Wood</option>
                <option value="h4">Hybrid 4</option><option value="h5">Hybrid 5</option>
                <option value="i5">Iron 5</option><option value="i6">Iron 6</option><option value="i7">Iron 7</option><option value="i8">Iron 8</option><option value="i9">Iron 9</option>
                <option value="pw">Pitching Wedge</option><option value="gw">Gap Wedge</option><option value="sw">Sand Wedge</option><option value="lw">Lob Wedge</option>
            </select>
        </div>
        <div class="form-group"><label for="distance">Distance (meters)</label><input type="number" id="distance" name="distance" min="0" max="400" placeholder="Enter distance"></div>
        <div class="form-group"><div class="checkbox-group"><input type="checkbox" id="fail" name="fail"><label for="fail" style="margin: 0;">Failed shot</label></div></div>
        <button type="submit">Record Shot</button>
    </form>
    <div id="message"></div>
    <div class="recent-shots"><h3>Recent Shots</h3><div id="recentShots">Loading...</div></div>
    <script>
        const pinScreen = document.getElementById('pinScreen'), pinForm = document.getElementById('pinForm'), pinInput = document.getElementById('pin'), pinMessage = document.getElementById('pinMessage');
        function getStoredPin() { return localStorage.getItem('carryon_pin'); }
        function storePin(pin) { localStorage.setItem('carryon_pin', pin); }
        function showPinScreen() { pinScreen.classList.remove('hidden'); }
        function hidePinScreen() { pinScreen.classList.add('hidden'); }
        async function verifyPin(pin) { try { const r = await fetch('/api/verify-pin', { method: 'POST', headers: { 'X-Pin': pin } }); return r.ok; } catch { return false; } }
        pinForm.addEventListener('submit', async function(e) { e.preventDefault(); const pin = pinInput.value; if (await verifyPin(pin)) { storePin(pin); hidePinScreen(); loadRecentShots(); } else { pinMessage.textContent = 'Invalid PIN'; pinMessage.className = 'message error'; pinInput.value = ''; } });
        async function initAuth() { const storedPin = getStoredPin(); if (storedPin && await verifyPin(storedPin)) { hidePinScreen(); loadRecentShots(); } else { localStorage.removeItem('carryon_pin'); showPinScreen(); } }
        document.getElementById('date').valueAsDate = new Date();
        const failCheckbox = document.getElementById('fail'), distanceInput = document.getElementById('distance');
        failCheckbox.addEventListener('change', function() { distanceInput.disabled = this.checked; if (this.checked) distanceInput.value = ''; });
        document.getElementById('shotForm').addEventListener('submit', async function(e) {
            e.preventDefault(); const submitBtn = this.querySelector('button[type="submit"]'); submitBtn.disabled = true;
            const data = { date: document.getElementById('date').value, club: document.getElementById('club').value, fail: failCheckbox.checked };
            if (!data.fail) { const distance = parseInt(distanceInput.value); if (isNaN(distance)) { showMessage('Please enter a distance or mark as failed', 'error'); submitBtn.disabled = false; return; } data.distance = distance; }
            try {
                const response = await fetch('/api/shots', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Pin': getStoredPin() || '' }, body: JSON.stringify(data) });
                const result = await response.json();
                if (response.ok) { showMessage('Recorded: ' + data.club + ' - ' + (data.fail ? 'FAIL' : data.distance + 'm'), 'success'); distanceInput.value = ''; failCheckbox.checked = false; distanceInput.disabled = false; loadRecentShots(); }
                else if (response.status === 401) { localStorage.removeItem('carryon_pin'); showPinScreen(); showMessage('PIN expired', 'error'); }
                else { showMessage(result.detail || 'Error', 'error'); }
            } catch (err) { showMessage('Network error: ' + err.message, 'error'); }
            submitBtn.disabled = false;
        });
        function showMessage(text, type) { const msg = document.getElementById('message'); msg.textContent = text; msg.className = 'message ' + type; setTimeout(() => { msg.textContent = ''; msg.className = ''; }, 3000); }
        async function loadRecentShots() { try { const response = await fetch('/api/shots?limit=5', { headers: { 'X-Pin': getStoredPin() || '' } }); const data = await response.json(); const container = document.getElementById('recentShots'); if (data.shots.length === 0) { container.innerHTML = '<p>No shots yet</p>'; return; } container.innerHTML = data.shots.map(shot => '<div class="shot-item"><span class="shot-club">' + shot.club.toUpperCase() + '</span><span class="' + (shot.fail ? 'shot-fail' : 'shot-distance') + '">' + (shot.fail ? 'FAIL' : shot.distance + 'm') + '</span><span style="color:#999;font-size:12px">' + shot.date + '</span></div>').join(''); } catch (err) { document.getElementById('recentShots').innerHTML = '<p>Could not load shots</p>'; } }
        initAuth();
    </script>
</body>
</html>"""
