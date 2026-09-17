THREE_D_GRAPHER_BETA - Stable Engine
======================================
NumWorks Python | 6.09 KB | 320x240 kandinsky display

CHANGES FROM ORIGINAL:
  1. FILLED POLYGON FACES
     - Added scanline-based quad rasterizer (fill_quad_fast)
     - Each face is filled with a solid color based on its Z-height
     - Color gradient: low Z = dark blue, high Z = bright cyan
     - Wireframe overlaid on top for structure

  2. GRID REDUCED: 14x14 -> 8x8 (81 vertices vs 225)
     - Massive performance improvement
     - Fewer eval() calls, faster mesh generation
     - Still looks clean on 320x240 screen

  3. PERSPECTIVE PROJECTION
     - Original used orthographic (no depth scaling)
     - Beta adds perspective divide: screen = world * (zoom / cam_z)
     - Objects further from camera appear smaller (realistic 3D)

  4. FLAT ARRAY STORAGE
     - Original used mesh_matrix[r][c] (nested lists)
     - Beta uses flat mesh_x[], mesh_y[], mesh_z[] arrays
     - Faster iteration, less memory overhead on MicroPython

  5. SCREEN CLAMPING
     - All projected coordinates clamped to [0, 318] x [25, 238]
     - Prevents drawing outside viewport or into HUD area

  6. NaN/INF SAFETY
     - eval() results checked for math.isnan() and math.isinf()
     - Bad values default to 0.0 instead of crashing

  7. SIMPLIFIED LINE DRAWING
     - Removed 2x2 thick pixels (single pixel lines)
     - Step cap reduced from 50 to 35
     - Added 25px top margin for HUD display

CONTROLS:
  ARROWS  = Rotate
  +/-     = Zoom
  BACK    = Exit (changed from EXE)

RENDERING PIPELINE:
  1. Project all vertices (with perspective divide)
  2. Fill quad faces (Z-height color gradient)
  3. Draw wireframe grid overlay
  4. Draw RGB axes on top

LIMITATIONS:
  - No depth sorting (faces can overlap incorrectly)
  - No back-face culling (hidden faces still drawn)
  - Grid is hardcoded, not user-configurable
  - No view reset option
