"""
Visual Diagrams for Topics
ASCII art representations to help students understand data structures
"""

def get_topic_visual(topic_key: str) -> str:
    """Get ASCII visual diagram for a topic."""
    
    visuals = {
        'arraylist': """
```
ARRAYLIST - Dynamic Resizing

Initial Array (capacity = 4):
┌───┬───┬───┬───┐
│ A │ B │ C │ D │  ← Full!
└───┴───┴───┴───┘

Try to add 'E'... Need more space!

Step 1: Create larger array
┌───┬───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │   │   │   │   │  ← New array (capacity = 8)
└───┴───┴───┴───┴───┴───┴───┴───┘

Step 2: Copy all elements
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │   │   │   │   │  ← Copied!
└───┴───┴───┴───┴───┴───┴───┴───┘

Step 3: Add new element
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │ E │   │   │   │  ← 'E' added
└───┴───┴───┴───┴───┴───┴───┴───┘
```
""",
        
        'recursion': """
```
RECURSION - The Call Stack

factorial(3) calls factorial(2) calls factorial(1)
     ↓              ↓              ↓
  ┌─────┐        ┌─────┐        ┌─────┐
  │ n=3 │        │ n=2 │        │ n=1 │  ← Base case!
  │  ?  │        │  ?  │        │  1  │     Returns 1
  └─────┘        └─────┘        └─────┘
     ↑              ↑              
  Waits...      Waits...        
  
Now unwinding:
  ┌─────┐        ┌─────┐        
  │ n=3 │   ←    │ n=2 │   ←    Returns 1
  │  ?  │        │ 2*1 │        
  └─────┘        └─────┘        
     ↑              
  Returns 2       
  
Final:
  ┌─────┐        
  │ n=3 │        
  │ 3*2 │   = 6  
  └─────┘        

Each call waits on the call stack until the base case returns!
```
""",

        'queue': """
```
QUEUE - First In, First Out (FIFO)

The Coffee Shop Line:
  FRONT                              BACK
    ↓                                  ↓
  ┌─────┬─────┬─────┬─────┐
  │Alice│ Bob │Carol│Dave │  ← Everyone waits their turn
  └─────┴─────┴─────┴─────┘
    ↑                   ↑
  poll()             offer()
  (removes front)    (joins the back)
  peek() → "Alice"   (look at front WITHOUT removing)

  poll() → "Alice"   (she was first in line)

  After poll():
  ┌─────┬─────┬─────┐
  │ Bob │Carol│Dave │
  └─────┴─────┴─────┘
    ↑               ↑
  FRONT            BACK

  No cutting. No skipping. Fair and simple.

─────────────────────────────────────────────

PRIORITY QUEUE - The ER Triage Desk

  Arrival order:  1.Sprain  2.Chest Pain  3.Cold  4.Bleeding

  But the PriorityQueue reorders by urgency:

  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
  │ Chest Pain │  │  Bleeding  │  │   Sprain   │  │    Cold    │
  │ priority=1 │  │ priority=2 │  │ priority=3 │  │ priority=4 │
  │ (critical) │  │  (urgent)  │  │  (moderate) │  │   (minor)  │
  └────────────┘  └────────────┘  └────────────┘  └────────────┘
        ↑
  poll() always takes
  the highest priority
  (lowest number) first

  Arrival order IGNORED — priority wins!

  Java default: min-heap → smallest value exits first
  PriorityQueue<Integer> pq = new PriorityQueue<>();
  pq.offer(50); pq.offer(10); pq.offer(30);
  pq.poll() → 10   (not 50, even though 50 arrived first!)
```
"""
    }

    return visuals.get(topic_key, "")