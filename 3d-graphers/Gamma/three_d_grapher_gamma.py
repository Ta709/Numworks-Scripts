import math, kandinsky as kd, ion, time

GRID = 9
X_MIN, X_MAX = -8.0, 8.0
Y_MIN, Y_MAX = -8.0, 8.0
STEP_X = (X_MAX - X_MIN) / GRID
STEP_Y = (Y_MAX - Y_MIN) / GRID
NUM_VERTS = (GRID + 1) * (GRID + 1)

print("=== NUMWORKS 3D DUAL-COLOR ENGINE ===")
expr = input("z = f(x,y) [Default: sin(x)*cos(y)]: ").strip().replace(' ', '')
if not expr: expr = "sin(x)*cos(y)"

mesh_x, mesh_y, mesh_z = [], [], []
allowed = {"sin": math.sin, "cos": math.cos, "sqrt": math.sqrt, "exp": math.exp, "pi": math.pi, "abs": abs}

for r in range(GRID + 1):
    y_v = Y_MIN + (r * STEP_Y)
    for c in range(GRID + 1):
        x_v = X_MIN + (c * STEP_X)
        env = dict(allowed); env['x'], env['y'] = x_v, y_v
        try:
            z_v = float(eval(expr, {"__builtins__": None}, env))
            if math.isnan(z_v) or math.isinf(z_v): z_v = 0.0
        except:
            z_v = 0.0
        mesh_x.append(x_v)
        mesh_y.append(y_v)
        mesh_z.append(z_v)

proj_buf = [0] * (NUM_VERTS * 3)

# Quad index mapping with alternating colors
quad_indices = []
COLOR_BLUE = (60, 130, 220)
COLOR_GREEN = (40, 180, 120)

for r in range(GRID):
    for c in range(GRID):
        i1 = r * (GRID + 1) + c
        i2 = i1 + 1
        i3 = (r + 1) * (GRID + 1) + c + 1
        i4 = (r + 1) * (GRID + 1) + c
        tile_color = COLOR_GREEN if (r + c) % 2 == 0 else COLOR_BLUE
        quad_indices.append((i1, i2, i3, i4, tile_color))

NUM_QUADS = len(quad_indices)
# Pre-allocated list for depth sorting
quad_depths = [None] * NUM_QUADS

def fill_quad_fast(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p4_x, p4_y, col):
    min_y = max(25, min(p1_y, p2_y, p3_y, p4_y))
    max_y = min(238, max(p1_y, p2_y, p3_y, p4_y))
    if min_y >= max_y: return

    pts_x = (p1_x, p2_x, p3_x, p4_x)
    pts_y = (p1_y, p2_y, p3_y, p4_y)

    for y in range(min_y, max_y + 1, 2):
        x_min_l, x_max_l = 320, -1
        for i in range(4):
            x1, y1 = pts_x[i], pts_y[i]
            x2, y2 = pts_x[(i + 1) % 4], pts_y[(i + 1) % 4]
            if (y1 <= y < y2) or (y2 <= y < y1):
                if y1 != y2:
                    x_intersect = x1 + (y - y1) * (x2 - x1) // (y2 - y1)
                    if x_intersect < x_min_l: x_min_l = x_intersect
                    if x_intersect > x_max_l: x_max_l = x_intersect
        
        x_start = max(0, x_min_l)
        x_end = min(318, x_max_l)
        w = x_end - x_start + 1
        if w > 0:
            kd.fill_rect(x_start, y, w, 2, col)

def draw_line(x1, y1, x2, y2, col):
    if not (0 <= x1 < 318 and 0 <= x2 < 318 and 0 <= y1 < 238 and 0 <= y2 < 238): return
    dx, dy = x2 - x1, y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps > 35: steps = 35
    if steps == 0:
        kd.set_pixel(x1, y1, col); return
    x_inc, y_inc = dx / steps, dy / steps
    x, y = float(x1), float(y1)
    for _ in range(int(steps) + 1):
        ix, iy = int(x), int(y)
        if 0 <= ix < 319 and 25 <= iy < 239:
            kd.set_pixel(ix, iy, col)
        x += x_inc; y += y_inc

axis_len = 8.0
axis_vectors = [
    ((0.0, 0.0, 0.0), (axis_len, 0.0, 0.0), (255, 0, 0)),
    ((0.0, 0.0, 0.0), (0.0, axis_len, 0.0), (255, 128, 0)),
    ((0.0, 0.0, 0.0), (0.0, 0.0, axis_len), (128, 0, 255))
]

ax, ay, zoom = 0.6, 0.5, 90.0
redraw = True

while True:
    moved = False
    if ion.keydown(ion.KEY_LEFT): ay -= 0.10; moved = True
    if ion.keydown(ion.KEY_RIGHT): ay += 0.10; moved = True
    if ion.keydown(ion.KEY_UP): ax -= 0.10; moved = True
    if ion.keydown(ion.KEY_DOWN): ax += 0.10; moved = True
    if ion.keydown(ion.KEY_PLUS): zoom *= 1.12; moved = True
    if ion.keydown(ion.KEY_MINUS): zoom /= 1.12; moved = True
    if ion.keydown(ion.KEY_OK): ax, ay, zoom = 0.6, 0.5, 90.0; moved = True; time.sleep(0.15) # Reset View
    if ion.keydown(ion.KEY_BACK): break

    if not moved and not redraw:
        time.sleep(0.02)
        continue

    redraw = False
    kd.fill_rect(0, 25, 320, 215, (240, 240, 245))

    # Rotation Matrix
    cy, sy = math.cos(ay), math.sin(ay)
    cx, sx = math.cos(ax), math.sin(ax)

    r00, r01, r02 = cy, 0.0, -sy
    r10, r11, r12 = -sx * sy, cx, -sx * cy
    r20, r21, r22 = cx * sy, sx, cx * cy

    # 1. Transform & Project Vertices
    for i in range(NUM_VERTS):
        x_w, y_w, z_w = mesh_x[i], mesh_y[i], mesh_z[i]
        
        cam_x = r00 * x_w + r01 * y_w + r02 * z_w
        cam_y = r10 * x_w + r11 * y_w + r12 * z_w
        cam_z = r20 * x_w + r21 * y_w + r22 * z_w + 20.0

        f = zoom / max(1.0, cam_z)
        
        idx = i * 3
        proj_buf[idx] = max(0, min(318, int(cam_x * f + 160)))
        proj_buf[idx + 1] = max(25, min(238, int(cam_y * f + 120)))
        proj_buf[idx + 2] = int(cam_z * 100) # Depth stored for sorting

    # 2. Painter's Depth Calculation & Sort
    for q_idx in range(NUM_QUADS):
        i1, i2, i3, i4, tile_col = quad_indices[q_idx]
        avg_z = proj_buf[i1 * 3 + 2] + proj_buf[i2 * 3 + 2] + proj_buf[i3 * 3 + 2] + proj_buf[i4 * 3 + 2]
        quad_depths[q_idx] = (avg_z, i1, i2, i3, i4, tile_col)

    # Sort quads furthest to nearest (Back-to-Front)
    quad_depths.sort(key=lambda item: item[0], reverse=True)

    # 3. Draw Sorted Quads
    for avg_z, i1, i2, i3, i4, tile_col in quad_depths:
        idx1, idx2, idx3, idx4 = i1 * 3, i2 * 3, i3 * 3, i4 * 3
        
        x1, y1 = proj_buf[idx1], proj_buf[idx1 + 1]
        x2, y2 = proj_buf[idx2], proj_buf[idx2 + 1]
        x3, y3 = proj_buf[idx3], proj_buf[idx3 + 1]
        x4, y4 = proj_buf[idx4], proj_buf[idx4 + 1]

        shoelace = (x1*y2 - y1*x2) + (x2*y3 - y2*x3) + (x3*y4 - y3*x4) + (x4*y1 - y4*x1)
        if abs(shoelace) > 0:
            fill_quad_fast(x1, y1, x2, y2, x3, y3, x4, y4, tile_col)

    # 4. Wireframe Overlay
    grid_col = (20, 20, 30)
    for r in range(GRID + 1):
        for c in range(GRID + 1):
            i1 = (r * (GRID + 1) + c) * 3
            x1, y1 = proj_buf[i1], proj_buf[i1 + 1]
            if c < GRID:
                i2 = (r * (GRID + 1) + c + 1) * 3
                draw_line(x1, y1, proj_buf[i2], proj_buf[i2 + 1], grid_col)
            if r < GRID:
                i3 = ((r + 1) * (GRID + 1) + c) * 3
                draw_line(x1, y1, proj_buf[i3], proj_buf[i3 + 1], grid_col)

    # 5. Render RGB Axes
    for p1, p2, col in axis_vectors:
        rx1 = r00 * p1[0] + r01 * p1[1] + r02 * p1[2]
        ry1 = r10 * p1[0] + r11 * p1[1] + r12 * p1[2]
        rz1_cam = r20 * p1[0] + r21 * p1[1] + r22 * p1[2] + 20.0

        rx2 = r00 * p2[0] + r01 * p2[1] + r02 * p2[2]
        ry2 = r10 * p2[0] + r11 * p2[1] + r12 * p2[2]
        rz2_cam = r20 * p2[0] + r21 * p2[1] + r22 * p2[2] + 20.0

        f1, f2 = zoom / max(1.0, rz1_cam), zoom / max(1.0, rz2_cam)
        draw_line(int(rx1 * f1 + 160), int(ry1 * f1 + 120),
                  int(rx2 * f2 + 160), int(ry2 * f2 + 120), col)

    kd.draw_string("z = " + expr[:18] + " [OK:Reset]", 5, 5, (0, 0, 0), (240, 240, 245))
    time.sleep(0.01)
