import base64
with open('ref/50-image.png', 'rb') as f:
    print(base64.b64encode(f.read()).decode('utf-8')[:100])
