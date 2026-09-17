import math
import kandinsky as kd
import ion

sqrt, sin, cos, tan = math.sqrt, math.sin, math.cos, math.tan
log, exp, pi, e = math.log, math.exp, math.pi, math.e
asin, acos, atan = math.asin, math.acos, math.atan

allowed_math = {
    "sqrt": sqrt, "sin": sin, "cos": cos, "tan": tan,
    "log": log, "exp": exp, "pi": pi, "e": e, "abs": abs, "pow": pow,
    "asin": asin, "acos": acos, "atan": atan
}



def parse_bound(bound_str):
    bound_str = bound_str.strip().lower()
    if not bound_str: return 0.0
    try: return float(eval(bound_str, {"__builtins__": None}, allowed_math))
    except: return 0.0

def connect(x1, y1, x2, y2, color):
    """Draws lines quickly with strict screen-boundary clipping to stop lag."""
    if not (0 <= x1 < 320 or 0 <= x2 < 320 or 0 <= y1 < 240 or 0 <= y2 < 240):
        return
      
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps > 60: steps = 60
    if steps == 0:
        if 0 <= x1 < 320 and 0 <= y1 < 240: kd.set_pixel(x1, y1, color)
        return

      
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x1, y1
    for _ in range(int(steps) + 1):
        if 0 <= int(x) < 320 and 0 <= int(y) < 240:
            kd.set_pixel(int(x), int(y), color)
        x += x_inc
        y += y_inc

def calculate_volume():
    print("\n=== 3D WIRED REVOLUTIONS===")
    print("1: Disk | 2: Washer")
    method = input("Method (1-2): ")
    if method not in ('1', '2'): return

    a_str = input("Lower bound a: ")
    b_str = input("Upper bound b: ")
    a = parse_bound(a_str)
    b = parse_bound(b_str)
    
    print("\nUse syntax like: sqrt(x) or sin(x)")
    R_expr = input("Outer R(x) = ")
    r_expr = input("Inner r(x) = ") if method == '2' else "0"


  
    # Math Integral Calculations
    steps = 40
    dx = (b - a) / steps if steps > 0 else 1
    integral_sum = 0.0
    
    for i in range(steps):
        x_val = a + (i * dx)
        eval_env = {"x": x_val}
        for k in allowed_math: eval_env[k] = allowed_math[k]
        try:
            R_x = eval(R_expr, {"__builtins__": None}, eval_env)
            r_x = eval(r_expr, {"__builtins__": None}, eval_env) if method == '2' else 0.0
            integral_sum += ((R_x**2) - (r_x**2)) * dx
        except:
            print("\nMath Syntax Error!"); return




  #NORMAL output
    print("\n-------------------------")
    print("V =", round(math.pi * integral_sum, 5))
    print("Without pi =", round(integral_sum, 5))
    print("-------------------------")
    
    want_graph = input("Launch Solid 3D view? (y/n): ").lower()
    if want_graph != 'y': return


      
    #MESH SETTINGS
    slices = 16 
    points_per_ring = 12 
    x_center = (a + b) / 2
    
    angle_x = 0.5
    angle_y = 0.5
    pan_x = 160
    pan_y = 120
    zoom = 50 / (max(b - a, 1.0))

    print("\nARROWS: Rotate | +/-: Fast Zoom")
    print("Press OK or EXE to exit.")
    redraw = True


  
      #Moving arounf
    while True:
        moved = False
        if ion.keydown(ion.KEY_LEFT): angle_y -= 0.15; moved = True
        if ion.keydown(ion.KEY_RIGHT): angle_y += 0.15; moved = True
        if ion.keydown(ion.KEY_UP): angle_x -= 0.15; moved = True
        if ion.keydown(ion.KEY_DOWN): angle_x += 0.15; moved = True
        if ion.keydown(ion.KEY_PLUS): zoom *= 1.25; moved = True   
        if ion.keydown(ion.KEY_MINUS): zoom /= 1.25; moved = True  
        if ion.keydown(ion.KEY_OK) or ion.keydown(ion.KEY_EXE): break

        if not moved and not redraw:
            continue

        redraw = False
        kd.fill_rect(0, 0, 320, 240, (240, 240, 245))
        
        # Axis rendered
        axis_len = max(b - a, 2.0)
        axes = [
            ((-axis_len/2, 0, 0), (axis_len/2, 0, 0), (255, 0, 0)),    
            ((0, -axis_len, 0), (0, axis_len, 0), (255, 128, 0)),     
            ((0, 0, -axis_len), (0, 0, axis_len), (128, 0, 255))      
        ]
        
        for p1, p2, col in axes:
            rx1 = p1[0] * math.cos(angle_y) - p1[2] * math.sin(angle_y)
            rz1 = p1[0] * math.sin(angle_y) + p1[2] * math.cos(angle_y)
            ry1 = p1[1] * math.cos(angle_x) - rz1 * math.sin(angle_x)
            rx2 = p2[0] * math.cos(angle_y) - p2[2] * math.sin(angle_y)
            rz2 = p2[0] * math.sin(angle_y) + p2[2] * math.cos(angle_y)
            ry2 = p2[1] * math.cos(angle_x) - rz2 * math.sin(angle_x)
            connect(int(rx1 * zoom + pan_x), int(ry1 * zoom + pan_y),
                    int(rx2 * zoom + pan_x), int(ry2 * zoom + pan_y), col)

        # Mesh
        prev_outer_ring = None
        prev_inner_ring = None

        for s in range(slices + 1):
            x_val = a + (s * (b - a) / slices)
            eval_env = {"x": x_val}
            for k in allowed_math: eval_env[k] = allowed_math[k]
            try:
                R_x = eval(R_expr, {"__builtins__": None}, eval_env)
                r_x = eval(r_expr, {"__builtins__": None}, eval_env) if method == '2' else 0.0
            except: continue

            current_outer_ring = []
            current_inner_ring = []

            for p in range(points_per_ring + 1):
                theta = (p * 2 * math.pi) / points_per_ring
                cx = x_val - x_center
                
                cy, cz = R_x * math.cos(theta), R_x * math.sin(theta)
                rx = cx * math.cos(angle_y) - cz * math.sin(angle_y)
                rz = cx * math.sin(angle_y) + cz * math.cos(angle_y)
                ry = cy * math.cos(angle_x) - rz * math.sin(angle_x)
                current_outer_ring.append((int(rx * zoom + pan_x), int(ry * zoom + pan_y)))

                if method == '2':
                    cy_in, cz_in = r_x * math.cos(theta), r_x * math.sin(theta)
                    rx_i = cx * math.cos(angle_y) - cz_in * math.sin(angle_y)
                    rz_i = cx * math.sin(angle_y) + cz_in * math.cos(angle_y)
                    ry_i = cy_in * math.cos(angle_x) - rz_i * math.sin(angle_x)
                    current_inner_ring.append((int(rx_i * zoom + pan_x), int(ry_i * zoom + pan_y)))

            # one by one, no more for loops haha time spent debugging: 1hr..
            #Why does this work?..
            if s > 0:
                for p in range(points_per_ring):
                    connect(current_outer_ring[p][0], current_outer_ring[p][1],
                            current_outer_ring[p+1][0], current_outer_ring[p+1][1], (0, 80, 220))
                    if prev_outer_ring:
                        connect(current_outer_ring[p][0], current_outer_ring[p][1],
                                prev_outer_ring[p][0], prev_outer_ring[p][1], (0, 80, 220))
                    if method == '2':
                        connect(current_inner_ring[p][0], current_inner_ring[p][1],
                                current_inner_ring[p+1][0], current_inner_ring[p+1][1], (0, 150, 60))
                        if prev_inner_ring:
                            connect(current_inner_ring[p][0], current_inner_ring[p][1],
                                    prev_inner_ring[p][0], prev_inner_ring[p][1], (0, 150, 60))

            prev_outer_ring = current_outer_ring
            prev_inner_ring = current_inner_ring



#FINALLY!!
calculate_volume()
