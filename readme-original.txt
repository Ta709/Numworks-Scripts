THREE_D_GRAPHER - Original Version
====================================
NumWorks Python | 6.53 KB | 320x240 kandinsky display

WHAT IT DOES:
  Plots 3D surface wireframe meshes of z=f(x,y) functions with
  real-time rotation and zoom via calculator arrow keys.

MATH:
  - Accepts any f(x,y) expression using sin, cos, tan, sqrt, log,
    exp, asin, acos, atan, pi, e, abs, pow
  - Evaluates z over a 14x14 grid (225 sample points)
  - Rotation via inline trig: separate Y-axis then X-axis rotations
  - Orthographic projection (no perspective divide)

CONTROLS:
  ARROWS  = Rotate mesh (X and Y axes)
  +/-     = Zoom in/out
  EXE     = Exit

RENDERING:
  - Wireframe only, no filled faces
  - 2x2 pixel thick edges for visibility on low-res screen
  - Blue lines for X-axis grid, green lines for Y-axis grid
  - RGB axis indicators (Red=X, Orange=Y, Purple=Z)
  - Frame sync via time.sleep(0.03)

INPUT:
  User types expression, then X/Y bounds (defaults to [-4, 4])
  Falls back to sin(x)*cos(y) on empty input

LIMITATIONS:
  - No depth sorting (wireframe only, so no occlusion issues)
  - No filled surfaces (wireframe is see-through)
  - Rotation matrix not precomputed (inline trig per frame)
  - Steps capped at 50 for line drawing to prevent lag
  - 14x14 grid is dense, slower on complex expressions
