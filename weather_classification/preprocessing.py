import os
from imageio import imread
from imageio import imsave
from skimage.transform import resize
from skimage.color import rgb2gray
from skimage import img_as_ubyte
import re
import urllib.request
import json
import numpy as np
import pandas as pd


def resize_and_greyscale(orig_dir, station_dir, size=100):
    """Save resized (into a square of size x size) and greyscale copies of the images found in the
    'orig_dir/station_dir' directory into destination directories 'resources/images/resized/<station_dir>' and
    'resources/images/greyscale/<station_dir>' Note aspect ratio is not maintained during resizing """

    files = os.listdir(orig_dir + '/' + station_dir)
    for filename in files:
        img = imread(orig_dir + '/' + station_dir + "/" + filename)

        dir_path = "resources/images/resized/" + station_dir + "_" + str(size)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # resize to given size - we don't care about aspect ratio for this type of classification
        resized_img = resize(img, (size, size))
        imsave(dir_path + '/' + filename, img_as_ubyte(resized_img))

        dir_path = "resources/images/greyscale/" + station_dir + "_" + str(size)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # greyscale
        grey_img = rgb2gray(resized_img)
        imsave(dir_path + '/' + filename, img_as_ubyte(grey_img))

        print(filename)


def load_training_images(image_dir, labels_file, ignore_stations=None):
    """Loads the images at the given directory into two numpy arrays, one holding the X values of the flattened image
    and another holding the Y labels retrieved from dataset csv"""

    if ignore_stations is None:
        ignore_stations = []

    df = pd.read_csv(labels_file, dtype={'station': str, 'date': str, 'label': str})
    df.set_index(['station', 'date'], inplace=True)

    files = os.listdir(image_dir)
    X = []
    Y = []
    for filename in files:

        r = re.compile("RVAS_(\w+)_\w+_(\d{8})_(\d{4})Z")
        m = r.match(filename)
        station = m.group(1)
        date = m.group(2)
        time = m.group(3)

        if station in ignore_stations:
            continue

        # change obstime to top of the hour
        if not time.endswith("00"):
            time = time[:2] + "00"
        datetime = date+time

        # todo should we skip night time pics? how to determine sunset/sunrise

        x_i = load_training_image(image_dir, filename)

        X.append(x_i)
        Y.append(df.loc[(station, datetime), 'label'][0])

    return np.asarray(X), np.asarray(Y, dtype=str)


def load_training_image(folder, filename):
    """Loads the image at the given location into a flat numpy array."""

    x = imread(folder + "/" + filename)
    x = x.flatten()

    return x


def generate_labels_from_observations(image_dir, dataset, core_url="http://dw-dev.cmc.ec.gc.ca:8180"):
    """Generate the classification target labels by using the information in the weather observation found at the given
    core for the given images. Saves the label into a csv file of format <station>,<YYYYMMDDHHmm>,<label>"""
    files = os.listdir(image_dir)
    r = re.compile("RVAS_(\w+)_\w+_(\d{8})_(\d{4})Z")

    Y = []
    for filename in files:
        m = r.match(filename)
        station = m.group(1)
        datetime = m.group(2) + m.group(3)

        label = generate_label_from_observation(datetime, station, core_url)
        print("labelled", filename, label)
        Y.append([station, datetime, label])

    # save file
    df = pd.DataFrame.from_records(Y, columns=['station', 'date', 'label'], index=['station', 'date'])
    output_file = "resources/images/labels/" + dataset + ".csv"
    print("saving", output_file)
    df.to_csv(output_file)
    return df


def generate_label_from_observation(date, station, core_url="http://dw-dev.cmc.ec.gc.ca:8180"):
    """Generate the classification target label by using the information in the weather observation found at the given
    core for the given date and station. Returned label is one of 'snow', 'clear', 'msng', 'error'"""

    snow_depth_pkg_id = "1_11_174_2_5_3_0"
    min_snow = 1.0

    es_req_url = core_url + "/search/v2.0/dms_data+msc+observation+atmospheric+surface_weather+ca-1.1-ascii/templateSearch?from=" + date + "&to=" + date + "&query=(1_7_84_0_0_0_0.value.lowercase%3A" + station + ")"

    with urllib.request.urlopen(es_req_url) as response:
        obs = json.loads(response.read().decode('utf8').replace("'", '"'))

    snow_depth = "MSNG"

    if obs["hits"]["hits"] and snow_depth_pkg_id in obs["hits"]["hits"][0]["_source"]:
        snow_depth = obs["hits"]["hits"][0]["_source"][snow_depth_pkg_id][0]["value"]

    y = "msng"
    if snow_depth != "MSNG":
        if float(snow_depth) > min_snow:
            y = "snow"
        else:
            y = "clear"

    return y
