"""
Visual Diagrams for Data Structures
Generates ASCII art and Mermaid diagrams to help visualize concepts
"""

def get_queue_visual() -> str:
    """Get visual representation of a Queue"""
    return """
```
QUEUE (First-In-First-Out)
    
    FRONT                          BACK
      ↓                              ↓
    ┌───┬───┬───┬───┐
    │ A │ B │ C │ D │  ← Elements
    └───┴───┴───┴───┘
      ↑           ↑
   remove()    add()
   (dequeue)   (enqueue)

Example:
  queue.add("E")  → adds to BACK
  queue.remove()  → removes "A" from FRONT
```
"""

def get_stack_visual() -> str:
    """Get visual representation of a Stack"""
    return """
```
STACK (Last-In-First-Out)

    push()  pop()
      ↓      ↑
    ┌─────┐
    │  D  │  ← TOP (last in, first out)
    ├─────┤
    │  C  │
    ├─────┤
    │  B  │
    ├─────┤
    │  A  │  ← BOTTOM (first in, last out)
    └─────┘

Example:
  stack.push("E")  → adds to TOP
  stack.pop()      → removes "D" from TOP
```
"""

def get_linked_list_visual() -> str:
    """Get visual representation of a Linked List"""
    return """
```
LINKED LIST (Connected Nodes)

    HEAD
      ↓
    ┌────┬──┐    ┌────┬──┐    ┌────┬──┐    ┌────┬──┐
    │ 10 │ ●├───→│ 20 │ ●├───→│ 30 │ ●├───→│ 40 │ ✗│
    └────┴──┘    └────┴──┘    └────┴──┘    └────┴──┘
     data next    data next    data next    data null

Each node contains:
  - Data (the value)
  - Next (pointer to next node)

To insert: Just change pointers!
To delete: Just change pointers!
```
"""

def get_binary_search_visual() -> str:
    """Get visual representation of Binary Search"""
    return """
```
BINARY SEARCH (Divide and Conquer)

Array: [2, 4, 6, 8, 10, 12, 14, 16]  (MUST BE SORTED!)
Looking for: 10

Step 1: Check middle (8)
  [2, 4, 6, 8] | [10, 12, 14, 16]
              ↑
            8 < 10, search RIGHT half

Step 2: Check middle of right half (12)
  [10, 12, 14, 16]
       ↑
     12 > 10, search LEFT of 12

Step 3: Check 10
  [10]
   ↑
  Found it!

Each step eliminates HALF the remaining elements!
That's why it's O(log n) - very fast!
```
"""

def get_recursion_visual() -> str:
    """Get visual representation of Recursion"""
    return """
```
RECURSION (Function Calls Itself)

Example: factorial(3)

  factorial(3)
    ↓ calls
  3 * factorial(2)
        ↓ calls
      2 * factorial(1)
            ↓ calls
          1 (BASE CASE - stops!)
            ↑ returns 1
      2 * 1 = 2
        ↑ returns 2
  3 * 2 = 6
    ↑ returns 6

The Stack:
┌─────────────┐
│ factorial(3)│  ← pushed first
├─────────────┤
│ factorial(2)│  ← pushed second
├─────────────┤
│ factorial(1)│  ← pushed third, BASE CASE
└─────────────┘
     ↑ ↑ ↑
    pop pop pop (returns work back up)

Without base case → Stack Overflow!
```
"""

def get_topic_visual(topic_key: str) -> str:
    """
    Get visual diagram for a topic.
    
    Args:
        topic_key: Topic key like 'queue', 'stack', etc.
    
    Returns:
        ASCII art diagram as string
    """
    visuals = {
        'queue': get_queue_visual(),
        'stack': get_stack_visual(),
        'linked-list': get_linked_list_visual(),
        'binary-search': get_binary_search_visual(),
        'recursion': get_recursion_visual()
    }
    
    return visuals.get(topic_key, "# Visual not available for this topic")


def get_mermaid_diagram(topic_key: str) -> str:
    """
    Get Mermaid diagram code for a topic.
    These can be rendered in Streamlit with st.markdown
    """
    diagrams = {
        'queue': """
```mermaid
graph LR
    A[FRONT] --> B[Element 1]
    B --> C[Element 2]
    C --> D[Element 3]
    D --> E[Element 4]
    E --> F[BACK]
    
    G[remove] -.-> B
    H[add] -.-> E
    
    style A fill:#e1f5ff
    style F fill:#ffe1f5
```
""",
        'stack': """
```mermaid
graph TB
    A[TOP] --> B[Element 4 - Last In]
    B --> C[Element 3]
    C --> D[Element 2]
    D --> E[Element 1 - First In]
    E --> F[BOTTOM]
    
    style A fill:#ffe1e1
    style F fill:#e1ffe1
```
""",
        'linked-list': """
```mermaid
graph LR
    HEAD[HEAD] --> N1[Node 1<br/>data: 10<br/>next: →]
    N1 --> N2[Node 2<br/>data: 20<br/>next: →]
    N2 --> N3[Node 3<br/>data: 30<br/>next: →]
    N3 --> NULL[NULL]
    
    style HEAD fill:#e1f5ff
    style NULL fill:#ffe1e1
```
"""
    }
    
    return diagrams.get(topic_key, "")
