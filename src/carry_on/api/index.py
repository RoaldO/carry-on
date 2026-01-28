import os
from datetime import UTC, date as date_type, datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from pymongo import MongoClient

from carry_on.api.pin_security import hash_pin, needs_rehash, verify_pin as verify_pin_hash
from carry_on.infrastructure.repositories.mongo_stroke_repository import MongoStrokeRepository
from carry_on.services.stroke_service import StrokeService

load_dotenv()

app = FastAPI(title="CarryOn - Golf Stroke Tracker")

# MongoDB connection (lazy initialization for serverless)
_client: Optional[MongoClient] = None


def get_strokes_collection():
    """Get MongoDB collection, initializing connection if needed."""
    global _client
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    if _client is None:
        _client = MongoClient(uri)
    return _client.carryon.strokes


def get_ideas_collection():
    """Get MongoDB ideas collection, initializing connection if needed."""
    global _client
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    if _client is None:
        _client = MongoClient(uri)
    return _client.carryon.ideas


def get_users_collection():
    """Get MongoDB users collection, initializing connection if needed."""
    global _client
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    if _client is None:
        _client = MongoClient(uri)
    return _client.carryon.users


def get_stroke_service() -> StrokeService:
    """Get StrokeService with MongoDB repository."""
    collection = get_strokes_collection()
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    repository = MongoStrokeRepository(collection)
    return StrokeService(repository)


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user returned by verify_pin()."""

    id: str
    email: str
    display_name: str


def verify_pin(
    x_pin: str = Header(None), x_email: str = Header(None)
) -> AuthenticatedUser:
    """Verify PIN from request header and return authenticated user.

    Authenticates user by verifying X-Email + X-Pin headers against user's PIN in database.
    Returns AuthenticatedUser on success.
    """
    if not x_email or not x_pin:
        raise HTTPException(status_code=401, detail="Authentication required")

    users_collection = get_users_collection()
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    user = users_collection.find_one({"email": x_email.lower()})
    if not user or not verify_pin_hash(x_pin, user.get("pin_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    # Rehash if needed (on successful auth)
    if needs_rehash(user.get("pin_hash", "")):
        users_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"pin_hash": hash_pin(x_pin)}}
        )

    return AuthenticatedUser(
        id=str(user["_id"]),
        email=user["email"],
        display_name=user.get("display_name", ""),
    )


class StrokeCreate(BaseModel):
    club: str
    distance: Optional[int] = None
    fail: bool = False
    date: date_type = Field(default_factory=date_type.today)


class Stroke(BaseModel):
    id: str
    club: str
    distance: Optional[int] = None
    fail: bool = False


class IdeaCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000)


class EmailCheck(BaseModel):
    email: str = Field(..., min_length=1)


class ActivateRequest(BaseModel):
    email: str = Field(..., min_length=1)
    pin: str = Field(..., min_length=4, max_length=10)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    pin: str = Field(..., min_length=4, max_length=10)


@app.post("/api/check-email")
async def check_email(request: EmailCheck):
    """Check if email exists and get activation status."""
    users_collection = get_users_collection()
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    status = "activated" if user.get("activated_at") else "needs_activation"
    return {
        "status": status,
        "display_name": user.get("display_name", ""),
    }


@app.post("/api/activate")
async def activate_account(request: ActivateRequest):
    """Activate account by setting PIN."""
    users_collection = get_users_collection()
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    if user.get("activated_at"):
        raise HTTPException(status_code=400, detail="Account already activated")

    # Hash PIN before storing
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "pin_hash": hash_pin(request.pin),
                "activated_at": datetime.now(UTC).isoformat(),
            }
        },
    )

    return {
        "message": "Account activated successfully",
        "user": {
            "email": user["email"],
            "display_name": user.get("display_name", ""),
        },
    }


@app.post("/api/login")
async def login(request: LoginRequest):
    """Login with email and PIN."""
    users_collection = get_users_collection()
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    if not user.get("activated_at"):
        raise HTTPException(status_code=400, detail="Account not activated")

    # Check PIN using secure verification
    if not verify_pin_hash(request.pin, user.get("pin_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    # Rehash if using outdated algorithm
    if needs_rehash(user.get("pin_hash", "")):
        users_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"pin_hash": hash_pin(request.pin)}}
        )

    return {
        "message": "Login successful",
        "user": {
            "email": user["email"],
            "display_name": user.get("display_name", ""),
        },
    }


@app.get("/", response_class=HTMLResponse)
async def serve_form():
    """Serve the golf stroke entry form."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "public", "index.html")

    # For Vercel deployment, the file might be in a different location
    if not os.path.exists(html_path):
        html_path = os.path.join(os.path.dirname(__file__), "public", "index.html")

    if not os.path.exists(html_path):
        # Return inline HTML as fallback
        return get_inline_html()

    with open(html_path, "r") as f:
        return f.read()


@app.get("/ideas")
async def serve_ideas():
    """Redirect /ideas to /#ideas for tab navigation."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/#ideas", status_code=302)


@app.get("/api/me")
async def get_current_user(user: AuthenticatedUser = Depends(verify_pin)):
    """Get current authenticated user's profile information."""
    return {
        "email": user.email,
        "display_name": user.display_name,
    }


@app.post("/api/strokes")
async def create_stroke(
    stroke: StrokeCreate,
    user: AuthenticatedUser = Depends(verify_pin),
    service: StrokeService = Depends(get_stroke_service),
):
    """Record a new golf stroke."""
    try:
        stroke_id = service.record_stroke(
            user_id=user.id,
            club=stroke.club,
            stroke_date=stroke.date,
            distance=stroke.distance,
            fail=stroke.fail,
        )
    except ValueError as e:
        # Invalid club or missing distance
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": stroke_id.value,
        "message": "Stroke recorded successfully",
        "stroke": {
            "club": stroke.club,
            "distance": stroke.distance if not stroke.fail else None,
            "fail": stroke.fail,
            "date": stroke.date.isoformat(),
        },
    }


@app.get("/api/strokes")
async def list_strokes(
    limit: int = 20,
    user: AuthenticatedUser = Depends(verify_pin),
    service: StrokeService = Depends(get_stroke_service),
):
    """List recent strokes for the authenticated user."""
    strokes = service.get_user_strokes(user.id, limit)

    return {
        "strokes": [
            {
                "id": stroke.id.value if stroke.id else None,
                "club": stroke.club.value,
                "distance": stroke.distance.meters if stroke.distance else None,
                "fail": stroke.fail,
                "date": stroke.stroke_date.isoformat(),
                "created_at": stroke.created_at.isoformat()
                if stroke.created_at
                else None,
            }
            for stroke in strokes
        ],
        "count": len(strokes),
    }


@app.post("/api/ideas")
async def create_idea(idea: IdeaCreate, user: AuthenticatedUser = Depends(verify_pin)):
    """Submit a new idea."""
    ideas_collection = get_ideas_collection()
    if ideas_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    created_at = datetime.now(UTC).isoformat()
    doc = {
        "description": idea.description,
        "created_at": created_at,
        "user_id": user.id,
    }

    result = ideas_collection.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "message": "Idea submitted successfully",
        "idea": {
            "description": idea.description,
            "created_at": created_at,
        },
    }


@app.get("/api/ideas")
async def list_ideas(limit: int = 50, user: AuthenticatedUser = Depends(verify_pin)):
    """List submitted ideas for the authenticated user."""
    ideas_collection = get_ideas_collection()
    if ideas_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    ideas = []
    cursor = (
        ideas_collection.find({"user_id": user.id}).sort("created_at", -1).limit(limit)
    )

    for doc in cursor:
        ideas.append(
            {
                "id": str(doc["_id"]),
                "description": doc["description"],
                "created_at": doc["created_at"],
            }
        )

    return {"ideas": ideas, "count": len(ideas)}


def get_inline_html() -> str:
    """Return inline HTML for the form (fallback for Vercel)."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CarryOn - Golf Stroke Tracker</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><line x1='8' y1='4' x2='8' y2='30' stroke='%232d5a27' stroke-width='2' stroke-linecap='round'/><polygon points='10,4 26,9 10,14' fill='%232d5a27'/><ellipse cx='8' cy='30' rx='6' ry='2' fill='%232d5a27' opacity='0.3'/></svg>">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 400px; margin: 0 auto; padding: 20px; padding-bottom: 80px; background: #f5f5f5; }
        h1 { text-align: center; color: #2d5a27; margin: 0; }
        .header { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 30px; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .tab-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; background: white; border-top: 2px solid #ddd; max-width: 400px; margin: 0 auto; }
        .tab-bar.hidden { display: none; }
        .tab { flex: 1; padding: 12px; text-align: center; cursor: pointer; color: #666; background: none; border: none; font-size: 14px; }
        .tab.active { color: #2d5a27; font-weight: 600; background: #e8f5e6; border-top: 3px solid #2d5a27; margin-top: -1px; }
        .tab-icon { font-size: 20px; display: block; margin-bottom: 4px; }
        textarea { width: 100%; padding: 14px; font-size: 16px; border: 2px solid #ddd; border-radius: 8px; background: white; resize: vertical; min-height: 150px; font-family: inherit; }
        textarea:focus { outline: none; border-color: #2d5a27; }
        .char-counter { text-align: right; font-size: 12px; color: #666; margin-top: 4px; }
        .char-counter.warning { color: #dc3545; }
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
        .recent-strokes { margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; }
        .stroke-item { background: white; padding: 12px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .stroke-club { font-weight: 600; color: #2d5a27; }
        .stroke-distance { color: #666; }
        .stroke-fail { color: #dc3545; font-weight: 600; }
        #loginScreen { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: #f5f5f5; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; z-index: 100; }
        #loginScreen.hidden { display: none; }
        .login-form { width: 100%; max-width: 300px; }
        .step { display: none; }
        .step.active { display: block; }
        .welcome-name { text-align: center; color: #2d5a27; font-size: 14px; margin-bottom: 15px; }
        .back-button { background: none; border: none; color: #2d5a27; cursor: pointer; font-size: 14px; margin-bottom: 15px; padding: 0; width: auto; }
        .back-button:hover { text-decoration: underline; }
        .profile-section { background: white; border-radius: 12px; padding: 24px; margin-top: 20px; }
        .profile-section h2 { margin: 0 0 20px 0; color: #2d5a27; }
        .profile-info { margin-bottom: 30px; }
        .profile-field { margin-bottom: 16px; }
        .profile-field label { display: block; font-size: 12px; color: #666; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        .profile-field div { font-size: 18px; color: #333; }
        .logout-btn { background: #dc3545; }
        .logout-btn:active { background: #a71d2a; }
    </style>
</head>
<body>
    <div id="loginScreen">
        <h1>CarryOn</h1>
        <div class="login-form">
            <div id="stepEmail" class="step active">
                <form id="emailForm">
                    <div class="form-group"><label for="email">Email address</label><input type="email" id="email" name="email" placeholder="your@email.com" required></div>
                    <button type="submit">Continue</button>
                    <div id="emailMessage"></div>
                </form>
            </div>
            <div id="stepPin" class="step">
                <button type="button" class="back-button" id="backToEmail">&larr; Back</button>
                <div id="welcomeName" class="welcome-name"></div>
                <form id="pinForm">
                    <div class="form-group"><label for="pin" id="pinLabel">Enter PIN</label><input type="password" id="pin" name="pin" inputmode="numeric" pattern="[0-9]*" placeholder="PIN" minlength="4" required></div>
                    <div class="form-group" id="confirmPinGroup" style="display: none;"><label for="confirmPin">Confirm PIN</label><input type="password" id="confirmPin" name="confirmPin" inputmode="numeric" pattern="[0-9]*" placeholder="Confirm PIN" minlength="4"></div>
                    <button type="submit" id="pinSubmitBtn">Login</button>
                    <div id="pinMessage"></div>
                </form>
            </div>
        </div>
    </div>
    <div class="header"><h1>CarryOn</h1></div>
    <div id="strokesContent" class="tab-content active">
        <form id="strokeForm">
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
            <div class="form-group"><div class="checkbox-group"><input type="checkbox" id="fail" name="fail"><label for="fail" style="margin: 0;">Failed stroke</label></div></div>
            <button type="submit">Record Stroke</button>
        </form>
        <div id="message"></div>
        <div class="recent-strokes"><h3>Recent Strokes</h3><div id="recentStrokes">Loading...</div></div>
    </div>
    <div id="ideasContent" class="tab-content">
        <form id="ideaForm">
            <div class="form-group"><label for="ideaDescription">Your idea or feedback</label><textarea id="ideaDescription" name="description" maxlength="1000" placeholder="Share your idea for improving CarryOn..." required></textarea><div class="char-counter"><span id="charCount">1000</span> characters remaining</div></div>
            <button type="submit">Submit Idea</button>
        </form>
        <div id="ideaMessage"></div>
    </div>
    <div id="profileContent" class="tab-content">
        <div class="profile-section">
            <h2>Your Profile</h2>
            <div class="profile-info">
                <div class="profile-field"><label>Display Name</label><div id="profileName">Loading...</div></div>
                <div class="profile-field"><label>Email</label><div id="profileEmail">Loading...</div></div>
            </div>
            <button id="logoutBtn" class="logout-btn">Logout</button>
        </div>
    </div>
    <div id="tabBar" class="tab-bar hidden">
        <button class="tab active" data-tab="strokes"><span class="tab-icon">&#9971;</span>Strokes</button>
        <button class="tab" data-tab="ideas"><span class="tab-icon">&#128161;</span>Ideas</button>
        <button class="tab" data-tab="profile"><span class="tab-icon">&#128100;</span>Profile</button>
    </div>
    <script>
        const loginScreen = document.getElementById('loginScreen'), stepEmail = document.getElementById('stepEmail'), stepPin = document.getElementById('stepPin');
        const emailForm = document.getElementById('emailForm'), emailInput = document.getElementById('email'), emailMessage = document.getElementById('emailMessage');
        const pinForm = document.getElementById('pinForm'), pinInput = document.getElementById('pin'), confirmPinInput = document.getElementById('confirmPin');
        const confirmPinGroup = document.getElementById('confirmPinGroup'), pinMessage = document.getElementById('pinMessage');
        const pinLabel = document.getElementById('pinLabel'), pinSubmitBtn = document.getElementById('pinSubmitBtn'), welcomeName = document.getElementById('welcomeName');
        const tabBar = document.getElementById('tabBar'), tabs = document.querySelectorAll('.tab');
        const strokesContent = document.getElementById('strokesContent'), ideasContent = document.getElementById('ideasContent'), profileContent = document.getElementById('profileContent');
        const profileName = document.getElementById('profileName'), profileEmail = document.getElementById('profileEmail'), logoutBtn = document.getElementById('logoutBtn');
        let currentEmail = '', isActivation = false;
        function getStoredAuth() { const e = localStorage.getItem('carryon_email'), p = localStorage.getItem('carryon_pin'); return e && p ? { email: e, pin: p } : null; }
        function storeAuth(e, p) { localStorage.setItem('carryon_email', e); localStorage.setItem('carryon_pin', p); }
        function clearAuth() { localStorage.removeItem('carryon_email'); localStorage.removeItem('carryon_pin'); }
        function getStoredPin() { const a = getStoredAuth(); return a ? a.pin : ''; }
        function getStoredEmail() { const a = getStoredAuth(); return a ? a.email : ''; }
        function getAuthHeaders() { return { 'X-Pin': getStoredPin() || '', 'X-Email': getStoredEmail() }; }
        function showLoginScreen() { loginScreen.classList.remove('hidden'); tabBar.classList.add('hidden'); showStep('email'); }
        function hideLoginScreen() { loginScreen.classList.add('hidden'); tabBar.classList.remove('hidden'); }
        function showStep(s) { stepEmail.classList.remove('active'); stepPin.classList.remove('active'); (s === 'email' ? stepEmail : stepPin).classList.add('active'); }
        function showTab(tabName) { strokesContent.classList.toggle('active', tabName === 'strokes'); ideasContent.classList.toggle('active', tabName === 'ideas'); profileContent.classList.toggle('active', tabName === 'profile'); tabs.forEach(tab => { tab.classList.toggle('active', tab.dataset.tab === tabName); }); history.replaceState(null, '', '#' + tabName); if (tabName === 'profile') loadProfile(); }
        tabs.forEach(tab => { tab.addEventListener('click', () => showTab(tab.dataset.tab)); });
        function handleHashChange() { const hash = window.location.hash.slice(1); if (hash === 'ideas' || hash === 'strokes' || hash === 'profile') { showTab(hash); } else { showTab('strokes'); } }
        window.addEventListener('hashchange', handleHashChange);
        async function checkEmail(email) { try { const r = await fetch('/api/check-email', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) }); if (r.status === 404) return { status: 'not_found' }; return await r.json(); } catch { return { status: 'error' }; } }
        function parseErrorDetail(d) { return Array.isArray(d) ? d.map(e => e.msg).join(', ') : d; }
        async function activateAccount(email, pin) { try { const r = await fetch('/api/activate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, pin }) }); const data = await r.json(); if (data.detail) data.detail = parseErrorDetail(data.detail); return { ok: r.ok, data }; } catch { return { ok: false, data: { detail: 'Network error' } }; } }
        async function login(email, pin) { try { const r = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, pin }) }); const data = await r.json(); if (data.detail) data.detail = parseErrorDetail(data.detail); return { ok: r.ok, data }; } catch { return { ok: false, data: { detail: 'Network error' } }; } }
        emailForm.addEventListener('submit', async function(e) { e.preventDefault(); const email = emailInput.value.trim().toLowerCase(); emailMessage.textContent = ''; emailMessage.className = ''; const result = await checkEmail(email); if (result.status === 'not_found') { emailMessage.textContent = 'Email not registered. Contact administrator.'; emailMessage.className = 'message error'; return; } if (result.status === 'error') { emailMessage.textContent = 'Connection error. Please try again.'; emailMessage.className = 'message error'; return; } currentEmail = email; isActivation = result.status === 'needs_activation'; welcomeName.textContent = 'Welcome, ' + (result.display_name || email); if (isActivation) { pinLabel.textContent = 'Create your PIN'; confirmPinGroup.style.display = 'block'; confirmPinInput.required = true; pinSubmitBtn.textContent = 'Activate'; } else { pinLabel.textContent = 'Enter PIN'; confirmPinGroup.style.display = 'none'; confirmPinInput.required = false; pinSubmitBtn.textContent = 'Login'; } pinInput.value = ''; confirmPinInput.value = ''; pinMessage.textContent = ''; showStep('pin'); });
        document.getElementById('backToEmail').addEventListener('click', function() { showStep('email'); });
        pinForm.addEventListener('submit', async function(e) { e.preventDefault(); const pin = pinInput.value; pinMessage.textContent = ''; pinMessage.className = ''; if (isActivation) { if (pin !== confirmPinInput.value) { pinMessage.textContent = 'PINs do not match'; pinMessage.className = 'message error'; return; } const result = await activateAccount(currentEmail, pin); if (result.ok) { storeAuth(currentEmail, pin); hideLoginScreen(); loadRecentStrokes(); } else { pinMessage.textContent = result.data.detail || 'Activation failed'; pinMessage.className = 'message error'; } } else { const result = await login(currentEmail, pin); if (result.ok) { storeAuth(currentEmail, pin); hideLoginScreen(); loadRecentStrokes(); } else { pinMessage.textContent = result.data.detail || 'Invalid PIN'; pinMessage.className = 'message error'; pinInput.value = ''; } } });
        async function initAuth() { const auth = getStoredAuth(); if (auth) { const result = await login(auth.email, auth.pin); if (result.ok) { hideLoginScreen(); loadRecentStrokes(); return; } clearAuth(); } showLoginScreen(); }
        document.getElementById('date').valueAsDate = new Date();
        const failCheckbox = document.getElementById('fail'), distanceInput = document.getElementById('distance');
        failCheckbox.addEventListener('change', function() { distanceInput.disabled = this.checked; if (this.checked) distanceInput.value = ''; });
        document.getElementById('strokeForm').addEventListener('submit', async function(e) {
            e.preventDefault(); const submitBtn = this.querySelector('button[type="submit"]'); submitBtn.disabled = true;
            const data = { date: document.getElementById('date').value, club: document.getElementById('club').value, fail: failCheckbox.checked };
            if (!data.fail) { const distance = parseInt(distanceInput.value); if (isNaN(distance)) { showMessage('Please enter a distance or mark as failed', 'error'); submitBtn.disabled = false; return; } data.distance = distance; }
            try {
                const response = await fetch('/api/strokes', { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) });
                const result = await response.json();
                if (response.ok) { showMessage('Recorded: ' + data.club + ' - ' + (data.fail ? 'FAIL' : data.distance + 'm'), 'success'); distanceInput.value = ''; failCheckbox.checked = false; distanceInput.disabled = false; loadRecentStrokes(); }
                else if (response.status === 401) { clearAuth(); showLoginScreen(); showMessage('Session expired', 'error'); }
                else { showMessage(result.detail || 'Error', 'error'); }
            } catch (err) { showMessage('Network error: ' + err.message, 'error'); }
            submitBtn.disabled = false;
        });
        function showMessage(text, type) { const msg = document.getElementById('message'); msg.textContent = text; msg.className = 'message ' + type; setTimeout(() => { msg.textContent = ''; msg.className = ''; }, 3000); }
        async function loadRecentStrokes() { try { const response = await fetch('/api/strokes?limit=5', { headers: getAuthHeaders() }); const data = await response.json(); const container = document.getElementById('recentStrokes'); if (data.strokes.length === 0) { container.innerHTML = '<p>No strokes yet</p>'; return; } container.innerHTML = data.strokes.map(stroke => '<div class="stroke-item"><span class="stroke-club">' + stroke.club.toUpperCase() + '</span><span class="' + (stroke.fail ? 'stroke-fail' : 'stroke-distance') + '">' + (stroke.fail ? 'FAIL' : stroke.distance + 'm') + '</span><span style="color:#999;font-size:12px">' + stroke.date + '</span></div>').join(''); } catch (err) { document.getElementById('recentStrokes').innerHTML = '<p>Could not load strokes</p>'; } }
        const ideaForm = document.getElementById('ideaForm'), ideaDescription = document.getElementById('ideaDescription'), charCount = document.getElementById('charCount'), ideaMessage = document.getElementById('ideaMessage');
        ideaDescription.addEventListener('input', function() { const remaining = 1000 - this.value.length; charCount.textContent = remaining; charCount.parentElement.classList.toggle('warning', remaining < 100); });
        ideaForm.addEventListener('submit', async function(e) { e.preventDefault(); const submitBtn = this.querySelector('button[type="submit"]'); submitBtn.disabled = true; try { const response = await fetch('/api/ideas', { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify({ description: ideaDescription.value }) }); if (response.ok) { ideaMessage.textContent = 'Idea submitted! Thank you for your feedback.'; ideaMessage.className = 'message success'; ideaDescription.value = ''; charCount.textContent = '1000'; charCount.parentElement.classList.remove('warning'); } else if (response.status === 401) { clearAuth(); showLoginScreen(); ideaMessage.textContent = 'Session expired'; ideaMessage.className = 'message error'; } else { const result = await response.json(); ideaMessage.textContent = result.detail || 'Error'; ideaMessage.className = 'message error'; } } catch (err) { ideaMessage.textContent = 'Network error: ' + err.message; ideaMessage.className = 'message error'; } submitBtn.disabled = false; });
        async function loadProfile() { try { const response = await fetch('/api/me', { headers: getAuthHeaders() }); if (response.ok) { const data = await response.json(); profileName.textContent = data.display_name || 'Not set'; profileEmail.textContent = data.email; } else if (response.status === 401) { clearAuth(); showLoginScreen(); } } catch (err) { profileName.textContent = 'Error loading'; profileEmail.textContent = 'Error loading'; } }
        logoutBtn.addEventListener('click', function() { clearAuth(); showLoginScreen(); });
        handleHashChange();
        initAuth();
    </script>
</body>
</html>"""
