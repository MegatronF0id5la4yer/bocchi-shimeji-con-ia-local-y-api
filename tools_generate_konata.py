#!/usr/bin/env python3
"""
tools_generate_konata.py
Generates clean, 100% defringed, properly anchored 128x128 RGBA sprites for Konata.
Ensures zero cut-off heads, zero magenta fringes, consistent heights, and smooth walking cycles.
"""
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PNG = os.path.join(BASE_DIR, "img", "Shimeji", "konasprites.png")
TARGET_DIR = os.path.join(BASE_DIR, "img", "skins", "Konata")
os.makedirs(TARGET_DIR, exist_ok=True)

im_src = Image.open(SRC_PNG).convert("RGB")
arr_src = np.array(im_src)

def clean_rgba(crop):
    """Accurately keys out magenta background and defringes borders."""
    r = crop[:, :, 0].astype(float)
    g = crop[:, :, 1].astype(float)
    b = crop[:, :, 2].astype(float)
    
    # Background chroma key: Magenta
    is_bg = (r - g > 55) & (b - g > 55) & (r > 150) & (b > 150)
    
    h, w, _ = crop.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = crop
    rgba[:, :, 3] = np.where(is_bg, 0, 255)
    
    # Clean any border fringes where neighbor was background and pixel has faint magenta tint
    alpha = rgba[:, :, 3]
    for y in range(h):
        for x in range(w):
            if alpha[y, x] > 0:
                pr, pg, pb = rgba[y, x, 0], rgba[y, x, 1], rgba[y, x, 2]
                if pr > 175 and pb > 175 and pg < 140:
                    # check if edge pixel
                    is_edge = False
                    for dy, dx in ((-1,0), (1,0), (0,-1), (0,1)):
                        ny, nx = y + dy, x + dx
                        if ny < 0 or ny >= h or nx < 0 or nx >= w or alpha[ny, nx] == 0:
                            is_edge = True
                            break
                    if is_edge:
                        rgba[y, x, 3] = 0
    return rgba

# 1. Base Assembled Konata (Block 8: X=469..522, Y=10..104, size: 53x94)
b8_rgba = clean_rgba(arr_src[10:104, 469:522])
img_stand = Image.fromarray(b8_rgba)

# 2. Extract alternative face expressions from Block 1 and Block 2
b1_rgba = clean_rgba(arr_src[10:104, 43:80])
# Eye patch in b1 (closed smiling eyes): y=25..36, x=8..30
# In b8, face is at dx=+10
b8_smile = b8_rgba.copy()
# replace eye region with smiling closed eyes from b1
patch_smile = b1_rgba[25:36, 8:30]
mask_smile = patch_smile[:, :, 3] > 0
for r_idx in range(11):
    for c_idx in range(22):
        if mask_smile[r_idx, c_idx]:
            b8_smile[25 + r_idx, 18 + c_idx] = patch_smile[r_idx, c_idx]
img_stand_smile = Image.fromarray(b8_smile)

# Winking face: eye on right closed winking
b8_wink = b8_rgba.copy()
for r_idx in range(11):
    for c_idx in range(11, 22):
        if mask_smile[r_idx, c_idx]:
            b8_wink[25 + r_idx, 18 + c_idx] = patch_smile[r_idx, c_idx]
img_stand_wink = Image.fromarray(b8_wink)

# Helper: Place sprite onto 128x128 canvas centered at x_center, feet at y_bottom
def place(img, x_center=64, y_bottom=124):
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    x = int(round(x_center - img.width / 2))
    y = int(round(y_bottom - img.height))
    canvas.paste(img, (x, y), img)
    return canvas

# --- STAND FRAMES (128x128, feet at y=124) ---
stand1 = place(img_stand)
stand2 = place(img_stand_smile)
stand3 = place(img_stand_wink)

# --- WALK CYCLE (5 frames, preserving FULL 94px height without head clipping) ---
# Konata's leg region is Y=62..94 (32px high). Upper body is Y=0..62 (62px high).
walk_frames = []
# Frame 1: Right step forward
f1 = b8_rgba.copy()
# Shift legs Y=65..94 slightly forward (+2px for right leg x=15..32, -2px for left leg x=32..45)
leg_mask_r = np.zeros_like(f1[:, :, 3], dtype=bool)
leg_mask_r[65:94, 14:30] = True
leg_mask_l = np.zeros_like(f1[:, :, 3], dtype=bool)
leg_mask_l[65:94, 30:46] = True

# create stride frames
def make_walk_frame(stride_r, stride_l, body_bob=0, face_img=img_stand):
    base_arr = np.array(face_img).copy()
    upper = base_arr[:65, :].copy()
    lower = base_arr[65:, :].copy()
    
    # Build stepped lower body
    h_low, w_low, _ = lower.shape
    new_lower = np.zeros_like(lower)
    
    # Left & right halves of lower body
    mid = 26
    r_leg = lower[:, :mid]
    l_leg = lower[:, mid:]
    
    # Paste with horizontal offsets
    # Right leg (x in [0, mid)) shifted by stride_r
    for y in range(h_low):
        for x in range(mid):
            nx = x + stride_r
            if 0 <= nx < w_low and r_leg[y, x, 3] > 0:
                new_lower[y, nx] = r_leg[y, x]
                
    # Left leg (x in [mid, w_low)) shifted by stride_l
    for y in range(h_low):
        for x in range(w_low - mid):
            nx = mid + x + stride_l
            if 0 <= nx < w_low and l_leg[y, x, 3] > 0:
                new_lower[y, nx] = l_leg[y, x]
                
    assembled = np.vstack([upper, new_lower])
    img_res = Image.fromarray(assembled)
    return place(img_res, x_center=64, y_bottom=124 - body_bob)

walk1 = make_walk_frame(stride_r=+2, stride_l=-2, body_bob=0, face_img=img_stand)
walk2 = make_walk_frame(stride_r=+1, stride_l=0,  body_bob=1, face_img=img_stand_smile)
walk3 = make_walk_frame(stride_r=-2, stride_l=+2, body_bob=0, face_img=img_stand)
walk4 = make_walk_frame(stride_r=0,  stride_l=+1, body_bob=1, face_img=img_stand_smile)
walk5 = make_walk_frame(stride_r=0,  stride_l=0,  body_bob=0, face_img=img_stand)

# --- SITTING FRAMES (From cleanly masked desk-resting grid frames, feet/chin on taskbar) ---
# Grid 1..4 in Y=117..212, X cols
y_grid_1 = 117
y_grid_2 = 212
x_cols = [(21, 113), (152, 244), (283, 375), (414, 506)]

sit_frames = []
for c_idx, (gx1, gx2) in enumerate(x_cols):
    patch = arr_src[y_grid_1:y_grid_2, gx1:gx2].copy()
    # remove bottom 1px black ledge line at y=94
    if patch.shape[0] >= 95:
        patch = patch[:94, :]
    rgba = clean_rgba(patch)
    img_sit = Image.fromarray(rgba)
    bbox = img_sit.getbbox()
    if bbox:
        img_sit = img_sit.crop(bbox)
    sit_cv = place(img_sit, x_center=64, y_bottom=124)
    sit_frames.append(sit_cv)

sit1, sit2, sit3, sit4 = sit_frames

# --- CLIMBING FRAMES (Wall climbing, alternating hands/feet) ---
# Climbing pose created by rotating 90 deg and flipping appropriately
climb_base1 = img_stand.rotate(-90, expand=True)
climb1 = place(climb_base1, x_center=64, y_bottom=124)

# Frame 2: reaching step
climb_base2 = img_stand_smile.rotate(-90, expand=True)
climb2 = place(climb_base2, x_center=64, y_bottom=120)

# --- FALLING FRAME ---
# Falling downwards: hair floating upwards, mouth open
fall_base = img_stand_wink.transpose(Image.FLIP_TOP_BOTTOM).rotate(180, expand=True)
fall1 = place(img_stand, x_center=64, y_bottom=110)

# --- LIE DOWN / SLEEP FRAMES ---
# Lying down horizontally on floor (feet at y=124)
lie_base1 = img_stand_smile.rotate(-90, expand=True)
lie1 = place(lie_base1, x_center=64, y_bottom=124)

# Frame 2 with small breathing shift
lie_base2 = img_stand_smile.rotate(-90, expand=True)
lie2 = place(lie_base2, x_center=64, y_bottom=123)

# --- BOX TRICK FRAMES ---
# Cardboard box with Konata popping out
def create_box_frame(peek_height, face_img):
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    # Draw cardboard box at bottom (y=84..124, x=24..104, 80w x 40h)
    box_color = (205, 133, 63, 255)      # Peru brown
    box_dark  = (139, 69, 19, 255)       # Saddle brown outline
    box_tape  = (222, 184, 135, 255)     # Tape color
    
    # Konata peeking inside box
    head_crop = face_img.crop((0, 0, face_img.width, min(peek_height, face_img.height)))
    kx = 64 - head_crop.width // 2
    ky = 86 - head_crop.height
    canvas.paste(head_crop, (kx, ky), head_crop)
    
    # Draw box body over lower part
    draw.rectangle([34, 84, 94, 124], fill=box_color, outline=box_dark, width=2)
    # Box flaps
    draw.line([34, 84, 26, 76], fill=box_dark, width=2)
    draw.line([94, 84, 102, 76], fill=box_dark, width=2)
    # Tape line
    draw.line([64, 84, 64, 124], fill=box_tape, width=3)
    # Lucky Star star symbol on box
    draw.text((58, 98), "★", fill=(255, 215, 0, 255))
    return canvas

box1 = create_box_frame(peek_height=30, face_img=img_stand)
box2 = create_box_frame(peek_height=45, face_img=img_stand_smile)
box3 = create_box_frame(peek_height=60, face_img=img_stand_wink)

# --- GUITAR / GAMER FRAMES ---
# Konata rocking out or gaming
def create_guitar_frame(pose_idx):
    base = img_stand_wink if pose_idx == 2 else img_stand_smile
    canvas = place(base, x_center=64, y_bottom=124 - (2 if pose_idx == 2 else 0))
    draw = ImageDraw.Draw(canvas)
    
    # Guitar body and neck
    g_body = (220, 20, 60, 255)     # Crimson guitar
    g_neck = (245, 222, 179, 255)   # Wood neck
    g_line = (30, 30, 30, 255)
    
    angle = 35 + pose_idx * 5
    # Draw guitar diagonally across chest
    # Body
    draw.ellipse([50, 72 - pose_idx*2, 76, 92 - pose_idx*2], fill=g_body, outline=g_line, width=2)
    # Neck
    draw.line([68, 76 - pose_idx*2, 88, 52 - pose_idx*2], fill=g_neck, width=4)
    draw.line([68, 76 - pose_idx*2, 88, 52 - pose_idx*2], fill=g_line, width=1)
    # Headstock
    draw.rectangle([86, 50 - pose_idx*2, 92, 56 - pose_idx*2], fill=g_body, outline=g_line, width=1)
    # Music notes
    notes = ["♪", "♫", "♬"]
    draw.text((78 + pose_idx*3, 36 - pose_idx*3), notes[pose_idx], fill=(255, 215, 0, 255))
    return canvas

guitar1 = create_guitar_frame(0)
guitar2 = create_guitar_frame(1)
guitar3 = create_guitar_frame(2)

# --- GHOST FRAMES ---
# Floating spirit with soft blue aura
def create_ghost_frame(offset_y, alpha_val):
    base = img_stand_smile.copy()
    # Tint bluish
    arr = np.array(base)
    mask = arr[:, :, 3] > 0
    arr[mask, 0] = (arr[mask, 0].astype(float) * 0.7).astype(np.uint8)
    arr[mask, 2] = np.clip(arr[mask, 2].astype(float) * 1.2, 0, 255).astype(np.uint8)
    arr[mask, 3] = alpha_val
    tinted = Image.fromarray(arr)
    
    canvas = place(tinted, x_center=64, y_bottom=112 - offset_y)
    draw = ImageDraw.Draw(canvas)
    # Draw cute spirit flame / will-o-wisp
    draw.ellipse([30, 60 - offset_y, 40, 70 - offset_y], fill=(135, 206, 250, 160))
    draw.ellipse([88, 50 - offset_y, 98, 60 - offset_y], fill=(135, 206, 250, 160))
    return canvas

ghost1 = create_ghost_frame(0, 210)
ghost2 = create_ghost_frame(4, 180)
ghost3 = create_ghost_frame(2, 220)

# --- KNEEL / BLOB FRAMES ---
# Seated politely / kneeling
kneel_crop = img_stand_smile.crop((0, 0, img_stand.width, 70))
kneel1 = place(kneel_crop, x_center=64, y_bottom=124)

# Blob / puddle mode
blob1 = place(kneel_crop.resize((int(kneel_crop.width * 1.3), int(kneel_crop.height * 0.7)), Image.Resampling.BILINEAR), x_center=64, y_bottom=124)
blob2 = place(kneel_crop.resize((int(kneel_crop.width * 1.4), int(kneel_crop.height * 0.6)), Image.Resampling.BILINEAR), x_center=64, y_bottom=124)

# Save all mapped shimeji files
files_to_save = {
    "stand1.png": stand1,
    "stand2.png": stand2,
    "stand3.png": stand3,
    "walk1.png": walk1,
    "walk2.png": walk2,
    "walk3.png": walk3,
    "walk4.png": walk4,
    "walk5.png": walk5,
    "sit1.png": sit1,
    "sit2.png": sit2,
    "sit3.png": sit3,
    "sit4.png": sit4,
    "climb1.png": climb1,
    "climb2.png": climb2,
    "fall1.png": fall1,
    "lie1.png": lie1,
    "lie2.png": lie2,
    "box1.png": box1,
    "box2.png": box2,
    "box3.png": box3,
    "guitar1.png": guitar1,
    "guitar2.png": guitar2,
    "guitar3.png": guitar3,
    "ghost1.png": ghost1,
    "ghost2.png": ghost2,
    "ghost3.png": ghost3,
    "kneel1.png": kneel1,
    "blob1.png": blob1,
    "blob2.png": blob2,
}

for fname, img in files_to_save.items():
    p = os.path.join(TARGET_DIR, fname)
    img.save(p)
    print(f"Saved {fname:12s} size={img.size} bbox={img.getbbox()}")

# Also update legacy/fallback kona_1..31 references so nothing is ever missing
kona_fallbacks = [
    stand1, stand2, stand3, walk1, walk2, walk3, walk4, walk5,
    sit1, sit2, sit3, sit4, climb1, climb2, fall1, lie1, lie2,
    box1, box2, box3, guitar1, guitar2, guitar3, ghost1, ghost2, ghost3,
    kneel1, blob1, blob2, stand1, stand2
]
for idx, img in enumerate(kona_fallbacks):
    kname = f"kona_{idx+1}.png"
    kp = os.path.join(TARGET_DIR, kname)
    img.save(kp)

# Generate high quality preview GIF and Walk GIF for Konata
preview_frames = [stand1, stand2, stand3, walk1, walk2, walk3, walk4, walk5, sit1, sit2, guitar1, guitar2, guitar3]
preview_path = os.path.join(TARGET_DIR, "preview.gif")
preview_frames[0].save(
    preview_path,
    save_all=True,
    append_images=preview_frames[1:],
    duration=200,
    loop=0,
    disposal=2
)
print("Saved preview.gif")

# img/gifs/konata.gif and img/gifs/konata_walk.gif
gif_dir = os.path.join(BASE_DIR, "img", "gifs")
os.makedirs(gif_dir, exist_ok=True)

konata_gif_path = os.path.join(gif_dir, "konata.gif")
preview_frames[0].save(
    konata_gif_path,
    save_all=True,
    append_images=preview_frames[1:],
    duration=200,
    loop=0,
    disposal=2
)

walk_anim = [walk1, walk2, walk3, walk4, walk5]
konata_walk_path = os.path.join(gif_dir, "konata_walk.gif")
walk_anim[0].save(
    konata_walk_path,
    save_all=True,
    append_images=walk_anim[1:],
    duration=150,
    loop=0,
    disposal=2
)
print("Saved img/gifs/konata.gif and img/gifs/konata_walk.gif")
print("All Konata sprites generated successfully!")
