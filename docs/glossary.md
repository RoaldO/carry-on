# Ubiquitous Language Glossary

This glossary defines the domain terms used throughout the CarryOn application. These terms form the **ubiquitous language** - a shared vocabulary between developers and domain experts (golfers) that should be used consistently in code, documentation, and conversation.

## Terms

### Address
The act of a player positioning their body and club to prepare for a stroke.

### Fairway
The manicured path between the tee and the green.

### Green (Putting Green)
The destination area containing the hole/cup. This is where different rules of movement (putting) apply.

### Handicap
A numerical measure of a golfer's potential. It functions as a Value Object used to "normalize" scores between players of different skill levels.

### Hazard
Obstacles like "Bunkers" (sand traps) or "Water Hazards." These represent Policy changes in your code (e.g., penalty strokes or restricted movement).

### Lie
The position of the ball and the condition of the ground it is resting on.

### Par
The predetermined number of strokes an expert golfer is expected to need to complete a hole. This is your baseline for all scoring logic.

### Round
The primary Aggregate Root. It tracks the player's progress across 18 (or 9) holes.

### Stroke
A single act of hitting the ball. This is the fundamental unit of the domain.

### Tee Box
The designated starting area for a hole. In a digital model, this often carries attributes like "color" (pro, amateur, ladies) which dictate the total distance.

### Whiff (Air Shot)
If you swing with the intent to hit the ball but miss it entirely, it still counts as a stroke.

## Scoring Terminology

| Term | Definition | Logic |
|------|------------|-------|
| Ace | A hole-in-one. | `Strokes == 1` |
| Birdie | One stroke under par. | `Strokes == Par - 1` |
| Bogey | One stroke over par. | `Strokes == Par + 1` |
| Double Bogey | Two strokes over par. | `Strokes == Par + 2` |
| Eagle | Two strokes under par. | `Strokes == Par - 2` |
