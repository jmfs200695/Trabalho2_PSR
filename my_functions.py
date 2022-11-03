from random import randint

import cv2
import numpy as np
import copy
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim


def TrackBars(_, window):
    """
        Function that is called continuously to get the position of the 6 trackbars created for binarizing an image.
        The function returns these positions in a dictionary and in Numpy Arrays.
    """
    # Get ranges from trackbar and add to a dictionary
    b_min = cv2.getTrackbarPos('B min', window)
    b_max = cv2.getTrackbarPos('B max', window)
    g_min = cv2.getTrackbarPos('G min', window)
    g_max = cv2.getTrackbarPos('G max', window)
    r_min = cv2.getTrackbarPos('R min', window)
    r_max = cv2.getTrackbarPos('R max', window)

    limit = {'B': {'min': b_min, 'max': b_max},
             'G': {'min': g_min, 'max': g_max},
             'R': {'min': r_min, 'max': r_max}}

    # Convert the dict structure created before to numpy arrays, because is the structure that opencv uses it.
    min = np.array([limit['B']['min'], limit['G']['min'], limit['R']['min']])
    max = np.array([limit['B']['max'], limit['G']['max'], limit['R']['max']])

    return limit, min, max


def createMask(ranges, image):

    # Create an array for minimum and maximum values
    min = np.array([ranges['B']['min'], ranges['G']['min'], ranges['R']['min']])
    max = np.array([ranges['B']['max'], ranges['G']['max'], ranges['R']['max']])

    # Create a mask using the previously created array
    mask = cv2.inRange(image, min, max)

    return mask


def getCentroid(mask_original):

    # Defining maximum area and mask label
    maxArea = 0
    maxLabel = 0

    # You need to choose 4 or 8 for connectivity type
    connectivity = 4

    # Perform the operation
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_original, connectivity, cv2.CV_32S)

    # For each blob, find their area and compare it to the largest one
    for label in range(1, num_labels):
        # Find area
        area = stats[label, cv2.CC_STAT_AREA]

        # If the area is larger than the max area, replace it
        if area > maxArea:
            maxArea = area
            maxLabel = label

    # If there are blobs, the label has to be different from zero
    if maxLabel != 0:
        # Create a new mask and find its centroid
        mask = labels == maxLabel
        centroid = centroids[maxLabel]
    else:
        # If there are no blobs, the mask stays the same, and there are no centroids
        mask = mask_original
        centroid = None

    return mask, centroid


def maxArea(image, mask):

    # Determine image size
    h, w, _ = image.shape

    # Creating colour channels, using the mask as the green one
    b = np.zeros(shape=[h, w], dtype=np.uint8)
    g = mask.astype(np.uint8) * 255
    r = copy.deepcopy(b)

    # Merge the channels to create a green mask
    image_green = cv2.merge([b, g, r])

    return image_green


def findFormsCentroids(blank_image):
    blank_image = cv2.cvtColor(blank_image, cv2.COLOR_BGR2GRAY)

    # Threshold it so it becomes binary
    ret, binary = cv2.threshold(blank_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # You need to choose 4 or 8 for connectivity type
    connectivity = 4

    # Perform the operation
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity, cv2.CV_32S)

    centers = {}
    # For each blob, find the centroids
    for label in range(1, num_labels):
        # Find centroid
        centers[label] = centroids[label]

    return centers, labels

def drawNumericPaintImage(blank_image):
    """
    Generates a random pattern to colour
    :param blank_image:
    :return:
    """
    # Create forms in the blank image

    pts_rect = np.array([[10, 5], [10, 225], [50, 225], [50, 5]])
    pts_tria = np.array([[160, 10], [160, 200], [250, 100]])
    pts_hex = np.array([[325, 70], [325, 160], [410, 200], [500, 160], [500, 70], [410, 20]])

    cv2.polylines(img=blank_image, pts=[pts_rect], isClosed=True, color=(0, 0, 0), thickness=2)
    cv2.polylines(img=blank_image, pts=[pts_tria], isClosed=True, color=(0, 0, 0), thickness=2)
    cv2.polylines(img=blank_image, pts=[pts_hex], isClosed=True, color=(0, 0, 0), thickness=2)
    # Find the centroids of the regions to draw the color number
    centers, labels = findFormsCentroids(blank_image)

    # Start variables
    region_colors = {}
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]

    # Draw region color idx
    for centers_key, centers_value in centers.items():

        idx = randint(1, len(colors) + 1)
        region_colors[centers_key] = {}
        region_colors[centers_key]['idx'] = idx
        region_colors[centers_key]['color'] = colors[idx - 1]
        blank_image = cv2.putText(blank_image, str(idx), (int(centers_value[0]),
                                                          int(centers_value[1])),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)

    # Paint image to have the corrected image. After use this painted image to compare with our painting.
    painted_image = copy.deepcopy(blank_image)
    for region_color_key, region_color_value in region_colors.items():
        id = labels == region_color_key
        painted_image[id] = region_color_value['color']

    return blank_image, painted_image


def combine(blank_image, frame):

    # Create mask of white pixels
    mask = cv2.inRange(blank_image, np.array([255, 255, 255]), np.array([255, 255, 255]))
    mask = mask.astype(np.bool)

    # Draw in the original frame
    new_frame = copy.deepcopy(frame)
    new_frame[~mask] = blank_image[~mask]

    return new_frame


def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def compare_images(imageA, imageB, title):
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(imageA, imageB)
    s = ssim(imageA, imageB)
    # set up the figure
    fig = plt.figure(title)
    plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
    # show first image
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(imageA, cmap=plt.cm.gray)
    plt.axis("off")
    # show the second image
    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(imageB, cmap=plt.cm.gray)
    plt.axis("off")
    # show the images
    plt.show()


