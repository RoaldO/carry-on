# Ubiquitous Language Glossary

This glossary defines the domain terms used throughout the CarryOn application. These terms form the **ubiquitous language** - a shared vocabulary between developers and domain experts (golfers) that should be used consistently in code, documentation, and conversation.

## Terms

### Handicap
A numerical measure of a golfer's potential. It functions as a Value Object used to "normalize" scores between players of different skill levels.

### Round
The primary Aggregate Root. It tracks the player's progress across 18 (or 9) holes.

### Stroke
A single act of hitting the ball. This is the fundamental unit of the domain.
