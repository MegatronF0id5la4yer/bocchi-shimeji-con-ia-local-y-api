#!/usr/bin/env python3
import os
import shutil
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_transparent_gif(frame_paths, output_path, duration=180, target_size=(128, 128)):
    frames = []
    for fp in frame_paths:
        if not os.path.exists(fp):
            print(f"Warning: frame {fp} not found, skipping")
            continue
        im = Image.open(fp).convert("RGBA")
        if im.size != target_size:
            im = im.resize(target_size, getattr(getattr(Image, 'Resampling', Image), 'LANCZOS', Image.BICUBIC))
        
        # Transparent palette conversion
        alpha = im.split()[3]
        mask = Image.eval(alpha, lambda a: 255 if a > 32 else 0)
        im_rgb = im.convert("RGB")
        # Quantize to 255 colors, saving index 255 for transparency
        p_img = im_rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
        p_img.paste(255, Image.eval(mask, lambda a: 255 if a == 0 else 0))
        p_img.info['transparency'] = 255
        p_img.info['duration'] = duration
        frames.append(p_img)

    if not frames:
        print(f"Error: no valid frames for {output_path}")
        return False

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration,
        disposal=2,
        transparency=255,
        optimize=False
    )
    print(f"[OK] Generated: {output_path} ({len(frames)} frames, {target_size}, {duration}ms)")
    return True

def main():
    skins = {
        "Hachi": {
            "walk_frames": ["walk1.png", "walk2.png", "walk3.png", "walk4.png", "walk5.png"],
            "showcase_frames": [
                "stand1.png", "stand2.png", "walk1.png", "walk2.png", "walk3.png",
                "sit1.png", "sit2.png", "guitar1.png", "guitar2.png", "guitar3.png",
                "blob1.png", "ghost1.png"
            ],
            "slug": "hachi"
        },
        "Usagi": {
            "walk_frames": ["walk1.png", "walk2.png", "walk3.png", "walk4.png", "walk5.png"],
            "showcase_frames": [
                "stand1.png", "stand2.png", "walk1.png", "walk2.png", "walk3.png",
                "sit1.png", "sit2.png", "guitar1.png", "guitar2.png", "guitar3.png",
                "blob1.png", "ghost1.png"
            ],
            "slug": "usagi"
        },
        "Pusheen": {
            "walk_frames": ["walk1.png", "walk2.png", "walk3.png", "walk4.png", "walk5.png"],
            "showcase_frames": [
                "stand1.png", "stand2.png", "walk1.png", "walk2.png", "walk3.png",
                "sit1.png", "sit2.png", "guitar1.png", "guitar2.png", "guitar3.png",
                "blob1.png", "ghost1.png"
            ],
            "slug": "pusheen"
        }
    }

    for skin_name, info in skins.items():
        skin_dir = os.path.join(BASE_DIR, "img", "skins", skin_name)
        slug = info["slug"]

        # 1. Walk GIF
        walk_fps = [os.path.join(skin_dir, f) for f in info["walk_frames"]]
        walk_out = os.path.join(BASE_DIR, "img", "gifs", f"{slug}_walk.gif")
        create_transparent_gif(walk_fps, walk_out, duration=140)

        # 2. Main Showcase GIF for img/gifs
        showcase_fps = [os.path.join(skin_dir, f) for f in info["showcase_frames"]]
        main_out = os.path.join(BASE_DIR, "img", "gifs", f"{slug}.gif")
        create_transparent_gif(showcase_fps, main_out, duration=180)

        # 3. preview.gif in img/skins/<Skin>/
        preview_skin = os.path.join(skin_dir, "preview.gif")
        shutil.copyfile(main_out, preview_skin)
        print(f"[OK] Copied {main_out} -> {preview_skin}")

        # 4. preview.gif in android_app/app/src/main/assets/skins/<Skin>/
        android_skin_dir = os.path.join(BASE_DIR, "android_app", "app", "src", "main", "assets", "skins", skin_name)
        if os.path.isdir(android_skin_dir):
            preview_android = os.path.join(android_skin_dir, "preview.gif")
            shutil.copyfile(main_out, preview_android)
            print(f"[OK] Copied {main_out} -> {preview_android}")

if __name__ == "__main__":
    main()

