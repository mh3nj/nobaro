# ================================================================
#  NOBARO — tools/make_icon.py
#  Regenerates from public/logo.png:
#    • icon.ico             — Windows exe icon (multi-resolution)
#    • public/logo_512.png  — window/taskbar icon copy (iconphoto)
#    • public/logo_256.png  — About-dialog display copy
#
#  The display copies exist because Tk's PhotoImage renders the
#  6000px source logo blank, and PhotoImage.subsample() is broken
#  in some Tk builds (also produces a blank image).  Pre-scaling
#  with Pillow keeps the app itself dependency-free.
#
#  Usage:  python tools/make_icon.py
#  Requires Pillow:  pip install pillow
# ================================================================

import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC   = os.path.join(ROOT, "public", "logo.png")
ICO   = os.path.join(ROOT, "icon.ico")
LOGO  = os.path.join(ROOT, "public", "logo_512.png")
LOGO2 = os.path.join(ROOT, "public", "logo_256.png")

SIZES = [16, 24, 32, 48, 64, 128, 256]


def _square(img: Image.Image) -> Image.Image:
    """Crop to a centered square so the icon is not stretched."""
    w, h = img.size
    side = min(w, h)
    box = ((w - side) // 2, (h - side) // 2,
           (w + side) // 2, (h + side) // 2)
    return img.crop(box)


def main():
    if not os.path.isfile(SRC):
        sys.exit(f"Logo not found: {SRC}")

    img = _square(Image.open(SRC).convert("RGBA"))

    frames = [img.resize((s, s), Image.LANCZOS) for s in SIZES]
    frames[-1].save(ICO, format="ICO", sizes=[(s, s) for s in SIZES],
                    append_images=frames[:-1])
    print(f"Wrote {ICO} with sizes {SIZES}")

    img.resize((512, 512), Image.LANCZOS).save(LOGO)
    print(f"Wrote {LOGO} (512x512)")

    img.resize((256, 256), Image.LANCZOS).save(LOGO2)
    print(f"Wrote {LOGO2} (256x256)")


if __name__ == "__main__":
    main()
