from PIL import Image

img = Image.open('ref/50-image.png')
pixels = img.load()
w, h = img.size
print(f"Size: {w}x{h}")

bg = pixels[0, 0]
print(f"Background: {bg}")

min_x, max_x = w, 0
min_y, max_y = h, 0

for y in range(h):
    for x in range(w):
        if pixels[x, y] != bg:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y

print(f"Content bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
print(f"Bottom margin: {h - 1 - max_y}")
print(f"Top margin: {min_y}")
print(f"Left margin: {min_x}")
print(f"Right margin: {w - 1 - max_x}")
