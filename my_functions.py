import cv2
import numpy as np
import json
import copy


def TrackBars(_, window):
    """
    Function that is called continuously to get the position of the 6 trackbars created to binarize an image.
    The function returns these positions in a dictionary and in Numpy Arrays.
    :param _: Obligatory variable from OpenCV trackbars but assigned as a silent variable because will not be used.
    :param window: The name of the OpenCV window from where we need to get the values of the trackbars.
    Datatype: OpenCV object
    :return: The dictionary with the limits assigned in the trackbars. Convert the dictionary to numpy arrays because
    of OpenCV and return also.
    'limit' Datatype: Dict
    'min' Datatype: Numpy Array object
    'max' Datatype: Numpy Array object
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
    """
    Using a dictionary wth ranges, create a mask of an image respecting those ranges
    :param ranges: Dictionary generated in color_segmenter.py
    :param image: Cv2 image - UInt8
    :return mask: Cv2 image - UInt8
    """

    # Create an array for minimum and maximum values
    min = np.array([ranges['B']['min'], ranges['G']['min'], ranges['R']['min']])
    max = np.array([ranges['B']['max'], ranges['G']['max'], ranges['R']['max']])

    # Create a mask using the previously created array
    mask = cv2.inRange(image, min, max)

    return mask


def getCentroid(mask_original):
    """
    Create a mask with the largest blob of mask_original and return its centroid coordinates
    :param mask_original: Cv2 image - Uint8
    :return mask: Cv2 image - Bool
    :return centroid: List of 2 values
    """

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
    """
    Using a mask, create a green undertone to an image
    :param image: Cv2 image - Uint8
    :param mask: Cv2 image - Bool
    :return image: Cv2 image - Uint8
    """

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

    # For each blob, find the centroids
    for label in range(1, num_labels):
        # Find centroid
        centroids = centroids[label]

    return centroids, labels


def getNumericPaintImage(blank_image):
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
    centroids, labels = findFormsCentroids(blank_image)

    # Start variables
    region_colors = {}
    red = np.array([255, 0, 0], dtype=np.uint8)
    blue = np.array([0, 0, 255], dtype=np.uint8)


    # Draw region color idx
    for centroids_coordinates_key, centroid_coordinates_value in centroids_coordinates.items():
        idx = randint(1, len(colors) + 1)
        region_colors[centroids_coordinates_key] = {}
        region_colors[centroids_coordinates_key]['color_idx'] = idx
        region_colors[centroids_coordinates_key]['color'] = colors[idx - 1]
        blank_image = cv2.putText(blank_image, str(idx), (int(centroid[0]),
                                                          int(centroid[1])),
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 1, cv2.LINE_AA)

    # Paint image to have the corrected image. After use this painted image to compare with our painting.
    painted_image = copy.deepcopy(blank_image)
    for region_color_key, region_color_value in region_colors.items():
        mask = labels == region_color_key
        painted_image[mask] = region_color_value['color']

    return blank_image, painted_image
