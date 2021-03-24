from weather_classification.preprocessing import load_training_images

# input data
image_dir = "resources/images/resized/vkc"

X, Y = load_training_images(image_dir)