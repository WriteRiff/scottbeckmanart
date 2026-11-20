"""Split a tall screenshot into viewable chunks. Usage: python split.py file.png chunk_h scale"""
import sys
from PIL import Image
f, ch, sc = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
im = Image.open(f)
n = 0
for y in range(0, im.height, ch):
    part = im.crop((0, y, im.width, min(im.height, y + ch)))
    part = part.resize((int(part.width * sc), int(part.height * sc)))
    part.convert("RGB").save(f.replace(".png", f"_{n}.jpg"), quality=80)
    n += 1
print(n)
