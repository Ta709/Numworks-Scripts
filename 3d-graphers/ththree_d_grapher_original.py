import math
import kandinsky as kd
import ion
import time

# The set of math eq heh
sqrt, sin, cos, tan = math.sqrt, math.sin, math.cos, math.tan
log, exp, pi, e = math.log, math.exp, math.pi, math.e
asin, acos, atan = math.asin, math.acos, math.atan

allowed_math = {
    "sqrt": sqrt, "sin": sin, "cos": cos, "tan": tan,
    "log": log, "exp": exp, "pi": pi, "e": e, "abs": abs, "pow": pow,
    "asin": asin, "acos": acos, "atan": atan
}

def connect_thick(p1, p2, color):
    """Draws 2x2 double-stroke bold wireframe edges with strict screen boundary clipping."""
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    if not (0 <= x1 < 319 or 0 <= x2 < 319 or 0 <= y1 < 239 or 0 <= y2 < 239):
        return
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps > 50: steps = 50  # Cap interpolation steps to eliminate render lag
    if steps == 0:
        kd.fill_rect(x1, y1, 2, 2, color)
        return
    
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x1, y1
    for _ in range(int(steps) + 1):
        ix, iy = int(x), int(y)
        if 0 <= ix < 319 and 0 <= iy < 239:
            kd.set_pixel(ix, iy, color)
            kd.set_pixel(ix + 1, iy, color)
            kd.set_pixel(ix, iy + 1, color)
            kd.set_pixel(ix + 1, iy + 1, color)
        x += x_inc
        y += y_inc

def run_3d_mesh_engine():
    kd.fill_rect(0, 0, 320, 240, (240, 240, 245))
    print("================================")
    print("   NumWorks 3D Surface Engine   ")
    print("================================")
    
    # input
    print("Use syntax like: sin(x)*cos(y) or (x**2 - y**2)/4")
    z_expr = input("z = f(x,y) = ").strip().replace(' ', '')
    if not z_expr: z_expr = "sin(x)*cos(y)" # Safe fallback default

    # boundary setup
    try:
        x_min = float(input("X Minimum (e.g. -4): ") or "-4")
        x_max = float(input("X Maximum (e.g.  4): ") or "4")
        y_min = float(input("Y Minimum (e.g. -4): ") or "-4")
        y_max = float(input("Y Maximum (e.g.  4): ") or "4")
    except ValueError:
        print("Invalid bounds. Falling back to default [-4, 4]")
        x_min, x_max, y_min, y_max = -4.0, 4.0, -4.0, 4.0

    print("\nGenerating 3D spatial points matrix...")
    
    # Mesh ykyk ^^ 
    grid_size = 14 # Optimized structural segment resolution
    x_step = (x_max - x_min) / grid_size
    y_step = (y_max - y_min) / grid_size
    
    # Pre-compiled 
    mesh_matrix = []
    for r in range(grid_size + 1):
        row_points = []
        y_val = y_min + (r * y_step)
        for c in range(grid_size + 1):
            x_val = x_min + (c * x_step)
            eval_env = {"x": x_val, "y": y_val, "max": max}
            for k in allowed_math: eval_env[k] = allowed_math[k]
            try:
                z_val = float(eval(z_expr, {"__builtins__": None}, eval_env))
            except:
                z_val = 0.0
            row_points.append((x_val, y_val, z_val))
        mesh_matrix.append(row_points)

    print("\n[Controls]: ARROWS=Rotate Space | +/-=Scale Zoom")
    input("Press EXE to run model loop...")

    # Viewport int naught
    angle_x = 0.6
    angle_y = 0.5
    pan_x, pan_y = 160, 130
    zoom = 120.0 / max(x_max - x_min, 1.0)
    
    # Define length by contraint
    axis_len = max(x_max - x_min, 4.0)
    # Custom axis ((start), (end), color) hehh
    axis_vectors = [
        ((0.0, 0.0, 0.0), (axis_len, 0.0, 0.0), (255, 0, 0)),     # X-axis (Red)
        ((0.0, 0.0, 0.0), (0.0, axis_len, 0.0), (255, 128, 0)),   # Y-axis (Orange)
        ((0.0, 0.0, 0.0), (0.0, 0.0, axis_len), (128, 0, 255))    # Z-axis (Purple)
    ]

    redraw = True

    while True:
        moved = False
        
        if ion.keydown(ion.KEY_LEFT): angle_y -= 0.12; moved = True
        if ion.keydown(ion.KEY_RIGHT): angle_y += 0.12; moved = True
        if ion.keydown(ion.KEY_UP): angle_x -= 0.12; moved = True
        if ion.keydown(ion.KEY_DOWN): angle_x += 0.12; moved = True
        if ion.keydown(ion.KEY_PLUS): zoom *= 1.2; moved = True
        if ion.keydown(ion.KEY_MINUS): zoom /= 1.2; moved = True
        if ion.keydown(ion.KEY_OK) or ion.keydown(ion.KEY_EXE): break
        
        if not moved and not redraw:
            continue

        redraw = False
        # white bkg
        kd.fill_rect(0, 0, 320, 240, (240, 240, 245))
        
        # Step1
        projected_matrix = []
        for r in range(grid_size + 1):
            row_scr = []
            for c in range(grid_size + 1):
                mx, my, mz = mesh_matrix[r][c]
                
                # 3D Matrix Rotational coords
                rx = mx * math.cos(angle_y) - mz * math.sin(angle_y)
                rz = mx * math.sin(angle_y) + mz * math.cos(angle_y)
                ry = my * math.cos(angle_x) - rz * math.sin(angle_x)
                
                # Map coordinates onto 2D view
                sx = int(rx * zoom + pan_x)
                sy = int(ry * zoom + pan_y)
                row_scr.append((sx, sy))
            projected_matrix.append(row_scr)

        # step2
        for p1, p2, col in axis_vectors:
            # Transform start point
            rx1 = p1[0] * math.cos(angle_y) - p1[2] * math.sin(angle_y)
            rz1 = p1[0] * math.sin(angle_y) + p1[2] * math.cos(angle_y)
            ry1 = p1[1] * math.cos(angle_x) - rz1 * math.sin(angle_x)
            
            # Transform end point
            rx2 = p2[0] * math.cos(angle_y) - p2[2] * math.sin(angle_y)
            rz2 = p2[0] * math.sin(angle_y) + p2[2] * math.cos(angle_y)
            ry2 = p2[1] * math.cos(angle_x) - rz2 * math.sin(angle_x)
            
            # Draw individual axis projection strands
            connect_thick((int(rx1 * zoom + pan_x), int(ry1 * zoom + pan_y)),
                          (int(rx2 * zoom + pan_x), int(ry2 * zoom + pan_y)), col)

        # step 3
        for r in range(grid_size + 1):
            for c in range(grid_size + 1):
                # Horizontal structural links -BLUe
                if c < grid_size:
                    connect_thick(projected_matrix[r][c], projected_matrix[r][c+1], (0, 80, 220))
                # Vertical structural links -Green
                if r < grid_size:
                    connect_thick(projected_matrix[r][c], projected_matrix[r+1][c], (0, 150, 60))

        # Floating HUD banner details
        display_str = "z = " + z_expr
        if len(display_str) > 31: display_str = display_str[:28] + "..."
        kd.draw_string(display_str, 10, 8, (0, 0, 0), (240, 240, 245))
        time.sleep(0.03) # Frame synchronization lock 

    print("\nEngine deactivated successfully.")

run_3d_mesh_engine()
