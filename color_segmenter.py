import json
from functools import partial
from colorama import Fore, Back, Style
from my_functions import *
from termcolor import cprint


def main():
    # Webcam video capture
    capture = cv2.VideoCapture(0)  # Camera 0 selected

    # Create windows
    window_1 = 'Camera'
    cv2.namedWindow(window_1, cv2.WINDOW_AUTOSIZE)
    window_2 = 'Mask'
    cv2.namedWindow(window_2, cv2.WINDOW_AUTOSIZE)

    if capture.isOpened() is True:
        # Use partial function for the trackbars
        TrackBars_partial = partial(TrackBars, window=window_1)

        # Create trackbars to control the threshold to binarize
        cv2.createTrackbar('B min', window_1, 0, 255, TrackBars_partial)
        cv2.createTrackbar('B max', window_1, 0, 255, TrackBars_partial)
        cv2.createTrackbar('G min', window_1, 0, 255, TrackBars_partial)
        cv2.createTrackbar('G max', window_1, 0, 255, TrackBars_partial)
        cv2.createTrackbar('R min', window_1, 0, 255, TrackBars_partial)
        cv2.createTrackbar('R max', window_1, 0, 255, TrackBars_partial)

        # Set the trackbars positions to 255 for maximum trackbars
        cv2.setTrackbarPos('B max', window_1, 255)
        cv2.setTrackbarPos('G max', window_1, 255)
        cv2.setTrackbarPos('R max', window_1, 255)

        # Hotkeys
        cprint('Color_segmenter is on.'
               , color='white')
        print('\nUse the trackbars to define the threshold limits as you wish.')
        print(Back.GREEN + '\nStart capturing the webcam video.' + Back.RESET)
        print(Fore.GREEN + '\nPress "w" to exit and save the threshold' + Fore.RESET)
        print(Fore.RED + 'Press "q" to exit without saving the threshold' + Fore.RESET)
    else:
        print(Back.RED + "WARNING!" + Back.RESET + Fore.RED + " Camera is off" + Fore.RESET)

    while capture.isOpened():

        # Get an image from the camera (a frame) and show it
        _, frame = capture.read()
        cv2.imshow(window_1, frame)

        # Get ranges from trackbars in dict and numpy data structures
        limit, min, max = TrackBars_partial(0)

        # Create mask using cv2.inRange. The output is still in uint8
        mask_frame = cv2.inRange(frame, min, max)

        # Show segmented image
        cv2.imshow(window_2, mask_frame)  # Display the image

        key = cv2.waitKey(1)  # Wait a key to stop the program

        # Keyboard inputs to finish
        if key == ord('q'):
            print(Fore.RED + '"q" (quit) pressed, exiting the program without saving' + Fore.RESET)
            break
        elif key == ord('w'):
            print(Fore.GREEN + '"w" (write) pressed, exiting the program and saving' + Fore.RESET)
            file_name = 'limits.json'
            with open(file_name, 'w') as file_handle:
                print("Creating file with threshold limits" + file_name)
                json.dump(limit, file_handle)

            break
    # When finished close all
    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
