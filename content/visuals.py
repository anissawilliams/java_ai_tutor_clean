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
"""
    }
    
    return visuals.get(topic_key, "")
