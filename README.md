# mosaic.py
basic prototype for creating a mosaic from an image

### requirements
PIL/Pillow  
scipy

### usage
1. get some images or create some with
```
from PIL import Image
for r in range(0, 255, 30):
        for g in range(0, 255, 30):
            for b in range(0, 255, 30):
			    i = Image.new("RGB", (10, 10), color=(r, g, b))
			    i.save("samples/%02x%02x%02x.png" % (r, g, b))
```
2. find dominant colors in those images
```
$ python analyze.py > image_colors.csv
```
3. create a mosaic for <input_image>
```
$ python mosaic.py <input_image> out.png
```