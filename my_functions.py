import copy
from collections import namedtuple

import cv2
import numpy as np


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
