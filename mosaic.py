import sys
from os import path
from rgb2lab import rgb2lab
from PIL import Image, ImageOps
from time import time
from scipy.spatial import KDTree


start_time = time()

# our image-pool.
# filename and precalculated dominant color valiues in L*a*b color space
color_map = []
with open("image_colors.csv", "r") as f:
	for line in f:
		fn, l, a, b = line.split(",")
		color_map.append([fn, [float(l), float(a), float(b)]])


def get_image(fn, sz):
	cache_fn = "img_cache/%s_%s" % (sz, path.split(fn)[1])
	if path.exists(cache_fn):
		return Image.open(cache_fn)
	pixel_image = Image.open(fn)
	max_square_size = (min(pixel_image.size), min(pixel_image.size))
	img = ImageOps.fit(pixel_image, max_square_size, Image.ANTIALIAS)
	img = img.resize((sz, sz), Image.ANTIALIAS)
	img.save(cache_fn)
	return img


def find_substitudes_kdtree_bulk(img):
	print "%.2f preparing KD-Tree" % (time() - start_time)
	values = [x[1] for x in color_map]
	t = KDTree(values)
	print "%.2f converting colors" % (time() - start_time)
	lab_colors = [rgb2lab(p) for p in img.getdata()]
	print "%.2f finding substitutes" % (time() - start_time)
	distances, indices = t.query(lab_colors)
	return [color_map[i] for i in indices]


def find_substitudes_kdtree(img):
	pixel_substitudes = []
	values = [x[1] for x in color_map]
	t = KDTree(values)
	for p in img.getdata():
		c = rgb2lab(p)
		d, i = t.query(c)
		pixel_substitudes.append(color_map[i])
	return pixel_substitudes


# brute force.. / most naive way to find closest neighbour
def find_substitudes_naive(img):
	# euclidian distance in 3d
	# no need for sqrt since we are only comparing
	def dist(p, q):
		d = (p[0] - q[0]) * (p[0] - q[0])
		d += (p[1] - q[1]) * (p[1] - q[1])
		d += (p[2] - q[2]) * (p[2] - q[2])
		return d

	pixel_substitudes = []
	# iterate over all pixels and get nearest match out of our image-pool
	for i, p in enumerate(img.getdata()):
		pixel_substitudes.append(["", float("inf")])
		for candidate, coords in color_map:
			d = dist(rgb2lab(p), coords)
			if d < pixel_substitudes[i][1]:
				pixel_substitudes[i] = [candidate, d]
	return pixel_substitudes

FINDER_FUNC = find_substitudes_naive
FINDER_FUNC = find_substitudes_kdtree
FINDER_FUNC = find_substitudes_kdtree_bulk
PIXEL_SIZE = 10
input_image = sys.argv[1]
output_image = sys.argv[2]

print "%.2f preparing image" % (time() - start_time)
i = Image.open(input_image)
w, h = i.size
i = i.resize((w/PIXEL_SIZE, h/PIXEL_SIZE), Image.ANTIALIAS).convert("RGB")
# make sure we align on a PIXEL_SIZE boundary.
# this will crop the new image a bit, but that doesnt matter
out = Image.new("RGB", (w/PIXEL_SIZE*PIXEL_SIZE, h/PIXEL_SIZE*PIXEL_SIZE))
print "%.2f finding pixel substitutes" % (time() - start_time)

pixel = FINDER_FUNC(i)


print "%.2f creating mosaic" % (time() - start_time)
index = 0
# "replace" each pixel in input with his nearest match

out_w, out_h = out.size
for y in range(0, out_h, PIXEL_SIZE):
	for x in range(0, out_w, PIXEL_SIZE):
		filename = pixel[index][0]
		img = get_image(filename, PIXEL_SIZE)
		out.paste(img, (x, y))
		index = index + 1
out.save(output_image)
