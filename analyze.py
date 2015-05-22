import sys
from PIL import Image, ImageOps
import scipy
import scipy.misc
import scipy.cluster
from rgb2lab import rgb2lab

NUM_CLUSTERS = 3


def inspect(image):
	ar = scipy.misc.fromimage(image)
	shape = ar.shape
	# flatten array
	ar = ar.reshape(scipy.product(shape[:2]), shape[2])

	codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)

	vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
	counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

	index_max = scipy.argmax(counts)                    # find most frequent
	peak = codes[index_max]

	lab = tuple(rgb2lab(peak))
	return lab


if __name__ == "__main__":
	for fn in sys.argv[1:]:
		img = Image.open(fn)
		# make image square/cropping towards middle
		max_square_size = (min(img.size), min(img.size))
		img = ImageOps.fit(img, max_square_size, Image.ANTIALIAS)
		if max_square_size[0] > 150:
			img = img.resize((150, 150))
		l, a, b = inspect(img)
		print("%s,%f,%f,%f" % (fn, l, a, b))
