from weather_classification.preprocessing import load_training_images
import numpy as np

label_dir = "resources/images/labels/"
image_dir = "resources/images/resized/"

image_tar = "vkc_50.tar.gz"
label_file = "vkc.csv"

# unzip tar if needed

X, Y = load_training_images(image_dir+image_tar.replace(".tar.gz", ""), label_dir + label_file)

# drop images that have a label (Y) of msng
to_delete = Y == 'msng'
X = np.delete(X, to_delete, axis=0)
Y = np.delete(Y, to_delete, axis=0)