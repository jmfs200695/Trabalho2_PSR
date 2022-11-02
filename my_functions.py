
import cv2
import numpy as np
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


def createBlend(white_image, frame):
    """
    Blend the canvas with the real frame, placing the drawings on top of the real image
    :param frame: Cv2 image - Uint8
    :param white_image: Cv2 image - Uint8
    :return frame: Cv2 image - Uint8
    """
    # Create mask of white pixels
    mask = cv2.inRange(white_image, np.array([255, 255, 255]), np.array([255, 255, 255]))
    mask = mask.astype(np.bool)

    # Placing the drawing in the original frame
    frame_cp = copy.deepcopy(frame)
    frame_cp[~mask] = white_image[~mask]

    return frame_cp
