from tkinter import Image

import numpy as np
import pandas as pd

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

def ascii_to_image(topic_key: str):
    from PIL import Image, ImageDraw, ImageFont

    text = get_topic_visual(topic_key)

    # Use a REAL monospaced font (Menlo is default on macOS)
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)

    lines = text.split("\n")

    # Calculate image size
    max_width = max(font.getlength(line) for line in lines)
    line_height = font.getbbox("A")[3]
    img_height = line_height * len(lines) + 20

    img = Image.new("RGB", (int(max_width) + 20, img_height), "white")
    draw = ImageDraw.Draw(img)

    y = 10
    for line in lines:
        draw.text((10, y), line, font=font, fill="black")
        y += line_height

    img.save(f"{topic_key}.png")


def main():
    print(get_topic_visual("arraylist"))
    print(get_topic_visual("recursion"))
    ascii_to_image("arraylist")
    ascii_to_image("recursion")

main()