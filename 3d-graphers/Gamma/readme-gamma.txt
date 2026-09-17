THREE_D_GRAPHER_GAMMA - Dual-Color Engine
===========================================
NumWorks Python | 6.79 KB | 320x240 kandinsky display

CHANGES FROM BETA:
  1. PAINTER'S ALGORITHM (DEPTH SORTING)
     - Each quad's average Z-depth is computed after projection
     - Quads sorted back-to-front before drawing
     - Nearest faces drawn last, correctly occlude far faces
     - This is the biggest visual improvement over beta

  2. BACK-FACE CULLING (SHOELACE FORMULA)
     - Uses signed area of projected quad to determine winding order
     - If shoelace > 0, face is facing away from camera (skipped)
     - Eliminates ~50% of quad draws, big performance win
     - Prevents seeing "through" the mesh from the back

  3. PRECOMPUTED ROTATION MATRIX
     - Beta computed trig inline per vertex (6 trig calls per vertex)
     - Gamma precomputes 3x3 rotation matrix once per frame
     - All vertices transformed via matrix multiply (9 muls + 6 adds)
     - Cleaner math, easier to modify rotation order

  4. ALTERNATING CHECKERBOARD COLORS
     - Beta used Z-height gradient (all same hue)
     - Gamma uses alternating blue/green checkerboard tiles
     - More visual contrast, easier to see mesh orientation
     - Pattern: COLOR_GREEN if (r+c)%2==0 else COLOR_BLUE

  5. DEPTH BUFFER IN PROJECTION
     - proj_buf stores 3 values per vertex: [screen_x, screen_y, cam_z]
     - cam_z multiplied by 100 for integer sorting precision
     - Used by painter's algorithm for correct draw order

  6. VIEW RESET
     - Press OK to reset angles and zoom to defaults (0.6, 0.5, 90.0)
     - 150ms sleep to prevent input bounce
     - Original and beta had no reset option

  7. GRID INCREASED: 8x8 -> 9x9 (100 vertices)
     - Slightly denser mesh than beta for better visual quality
     - Still much lighter than original's 14x14

CONTROLS:
  ARROWS  = Rotate
  +/-     = Zoom
  OK      = Reset view to defaults
  BACK    = Exit

RENDERING PIPELINE:
  1. Compute 3x3 rotation matrix
  2. Transform all vertices to camera space (matrix multiply)
  3. Project to screen with perspective divide
  4. Store depth in proj_buf for sorting
  5. Compute quad depths, sort back-to-front
  6. Draw quads with back-face culling (shoelace test)
  7. Draw wireframe overlay
  8. Draw RGB axes

COMPARISON SUMMARY:
  Original -> Beta:   Added filled faces, perspective, smaller grid
  Beta -> Gamma:      Added depth sorting, back-face culling, rotation matrix

  Original: Fast wireframe, no depth, 14x14 grid
  Beta:     Filled faces but wrong draw order, 8x8 grid
  Gamma:    Correct 3D rendering with proper occlusion, 9x9 grid
