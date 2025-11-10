# IKT213 Photo Looksmaxer

A Python photo editing application using Tkinter.

## Requirements
- Python 3.13 or higher
- Tkinter (comes with Python)
- External packages:
  - numpy
  - Pillow
  - opencv-python
  - rawpy
  - torch
  - torchvision
  - matplotlib
  - scikit-learn

> Note: This application has only been tested on Windows 11.

## Installation

1. Clone the repository:

With https:
```bash
git clone https://github.com/ShafqatAfzali/IKT213_prosjekt.git
cd IKT213_prosjekt
```

with ssh:
```bash
git clone git@github.com:ShafqatAfzali/IKT213_prosjekt.git
cd IKT213_prosjekt
```

2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Running the Program
```bash
python main.py
```

Notes: 
Tested with Python 3.13 on Windows 10.
Tkinter must be installed (usually included with Python).



## Usage Guide

1. **Start the application**  
```bash
python main.py
```

**Open an image**
- Go to File → Open
- Select an image file
- Click open in the file browser

**Basic editing**
- Image → Select for rectangular, free-form (Lasso), or polygon selections
  - Rectangle: click and drag
  - Polygon: left click for each point, right click to close
  - Lasso: click and drag, release to close
  - Press Escape to unselect
  - Filters apply only to the selected area (if any)
- Image → Rotate / Flip / Crop / Resize
- Tools → Filters to apply Gaussian, Sobel, Binary filters or Histogram thresholding 
  - Apply to whole image or selected area

**Drawing and shapes**
- Shapes → List of Shapes select shape
  - Click Enable Drawing to draw, Disable Drawing to stop
- Set outline and fill colors via Shapes → Outline Color / Fill Color
  - Note: Fill may not work correctly; colors are a work in progress
- Use Tools → Paint Brushes for freehand edits
- Undo/Redo: File → Undo / Redo or Ctrl+Z / Ctrl+Y
- Colors: adjust brush size and color via Brush Size and Choose Color

**Gradient**
- Local → Gradient
  - Hold left-click and across image in the wanted direction
    - Example drag Left to Right, left side gets darker and right side brighter

**Adjust brightness, contrast etc**
- Adjustments
  - Drag sliders or click buttons

**Save your work**
- File → Save overwrites the current file
- File → Save As exports a new copy

**Exit the app**
- File → Quit