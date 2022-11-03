#!/usr/bin/python3
import math

from colorama import Fore, Back, Style
from my_functions import *
from time import ctime
import json
import argparse


def onMouse(event, x, y, flags, param):
    """
    Mouse Coordinates when we press left button of the mouse
    """
    global ispressed, center_mouse

    if event == cv2.EVENT_MOUSEMOVE:
        if ispressed:
            center_mouse = (x, y)

    if event == cv2.EVENT_LBUTTONDOWN:
        ispressed = True
        center_mouse = (x, y)

    if event == cv2.EVENT_LBUTTONUP:
        ispressed = False
        center_mouse = None


def main():
    # Initialization

    global center_mouse, ispressed, cache, blank_original

    # Variables set up
    center_prev = (200, 200)
    color = (255, 0, 0)
    color_str = 'BLUE'
    size = 6
    cache = None
    start_point = None
    center_mouse = (200, 200)
    center_prev_mouse = (200, 200)
    ispressed = False
    mouse_painting = True
    start_point_mouse = None
    cache_mouse = None
    listmouse = []
    real_frame = False
    listkeys = []
    limit = 50

    # Webcam video capture
    capture = cv2.VideoCapture(0)  # Camera 0 selected
    ret, frame = capture.read()

    # Create argparse
    ap = argparse.ArgumentParser(description='Paint on Augmented Reality')
    ap.add_argument('-j', '--json', required=True, help="Input json file path")
    ap.add_argument('-usp', '--use_shake_prevention', action='store_true',
                    help='Select this option to use shake prevention.')
    ap.add_argument('-unp', '--use_numeric_painting', action='store_true',
                    help='Select this option to use numeric painting.')
    args = vars(ap.parse_args())

    # Open the JSON file
    with open(args['json']) as file_handle:
        # returns JSON object as a dictionary
        limits = json.load(file_handle)

    # Define shake prevention
    if args['use_shake_prevention']:  # if the user uses the shake prevention
        print(Fore.BLUE + Back.WHITE + 'You are using shake prevention.' + Style.RESET_ALL)
        shake_prevention = 1
    else:
        shake_prevention = 0

    if capture.isOpened() is True:

        # Hotkeys description
        print(
            Back.BLUE + '\nYou opened AR_PAINT' + Back.RESET +
            Back.GREEN + '\nCapturing with the webcam.' + Back.RESET +
            '\n\nBy default you can start painting with the mouse. The color is ' + Fore.BLUE + color_str + Fore.RESET + ' and the pencil size is ' + Fore.LIGHTYELLOW_EX +
            str(size) + Fore.RESET +
            '\nPress and hold the left button of the mouse, to paint with the mouse' +
            '\n\nTo change the color of the pencil to: ' + Fore.RED + '\n  red' + Fore.RESET
            + ' press the letter ' + Fore.RED + '"r"' + Style.RESET_ALL +
            Fore.GREEN + '\n  green' + Fore.RESET
            + ' press the letter ' + Fore.GREEN + '"  g"' + Style.RESET_ALL + Fore.BLUE + '\n  blue' + Fore.RESET
            + ' press the letter ' + Fore.BLUE + '"b"' + Style.RESET_ALL +
            '\n\nPress ' + Fore.LIGHTYELLOW_EX + '"+"' + Style.RESET_ALL + 'to increase pencil size' +
            '\nPress ' + Fore.LIGHTYELLOW_EX + '"-"' + Style.RESET_ALL + 'to decrease pencil size' +
            '\n\nPress ' + Fore.LIGHTYELLOW_EX
            + '"n"' + Style.RESET_ALL + ' to paint with the mask. \nPress ' + Fore.LIGHTYELLOW_EX + '"m"' + Style.RESET_ALL +
            ' to paint with the mouse. \nPress ' + Fore.LIGHTYELLOW_EX + '"w"' + Style.RESET_ALL +
            ' to save the current canvas to a .png file \nPress ' + Fore.LIGHTYELLOW_EX + '"c"' + Style.RESET_ALL +
            ' to clear the canvas. \nPress ' + Fore.LIGHTYELLOW_EX + '"q"' + Style.RESET_ALL +
            ' to quit the program.\n\nPress and hold ' + Fore.LIGHTYELLOW_EX + '"s"' + Style.RESET_ALL +
            ' to draw a rectangle \nPress and hold ' + Fore.LIGHTYELLOW_EX + '"o"' + Style.RESET_ALL + ' to draw a circle'
        )
    else:
        print(Back.RED + "WARNING!" + Back.RESET + Fore.RED + " Camera is off" + Fore.RESET)

    # Create white canvas
    window_width = frame.shape[1]
    window_height = frame.shape[0]
    blank_image = 255 * np.ones(shape=[window_height, window_width, 3], dtype=np.uint8)

    # Setup for numeric paint
    if args['use_numeric_painting']:
        # Print
        print(Back.GREEN + '\nAR_PAINT opened' + Back.RESET)

        # Colors to paint image
        colors = [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0)]
        # Generating the numeric picture
        pts_rect = np.array([[10, 5], [10, 225], [50, 225], [50, 5]])
        pts_tria = np.array([[160, 10], [160, 200], [250, 100]])
        pts_hex = np.array([[325, 70], [325, 160], [410, 200], [500, 160], [500, 70], [410, 20]])

        cv2.polylines(img=blank_image, pts=[pts_rect], isClosed=True, color=(0, 0, 0), thickness=2)
        cv2.polylines(img=blank_image, pts=[pts_tria], isClosed=True, color=(0, 0, 0), thickness=2)
        cv2.polylines(img=blank_image, pts=[pts_hex], isClosed=True, color=(0, 0, 0), thickness=2)

        # Find the centroids of the regions to draw the color number
        centers, labels = findFormsCentroids(blank_image)
        # Print to the user which color should he print in it index
        print('\nColor index 1 corresponds to ' + Fore.BLUE + 'blue ' + Fore.RESET + 'color.')
        print('Color index 2 corresponds to ' + Fore.GREEN + 'green ' + Fore.RESET + 'color.')
        print('Color index 3 corresponds to ' + Fore.RED + 'red' + Fore.RESET + 'color.')
        print('Color index 4 corresponds to ' + Fore.YELLOW + 'yellow ' + Fore.RESET + 'color.')
        print('Press the space bar to finish and see your evaluation...\n')

        # Defining the window and showing the painted image
        cv2.namedWindow('Painted Image', cv2.WINDOW_NORMAL)
        cv2.imshow('Painted Image', blank_image)

    cv2.namedWindow('Canvas', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Original', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Mask', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('MaxArea', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Canvas', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Canvas', blank_image)

    # Defining mouse callback
    cv2.setMouseCallback("Canvas", onMouse)

    # Execute
    while capture.isOpened():
        # Get and show frames from camera
        ret, frame = capture.read()
        frame = cv2.flip(frame, 1)

        # Create original mask
        mask_original = createMask(limits, frame)

        # Find centroid
        mask, centroid = getCentroid(mask_original)

        # Create a green mask for max area
        image_green = maxArea(frame, mask)

        # Wait a key to stop the program
        key = cv2.waitKey(1)

        # key to list
        listkeys.append(key)

        # Mouse position to list
        listmouse.append(center_mouse)

        # if a key is pressed
        if key != -1:

            # Press "b" for blue
            if key == ord('b'):
                color = (255, 0, 0)
                color_str = 'BLUE'
                print(Fore.BLUE + color_str + ' color selected.                                   ' + Style.RESET_ALL,
                      end='\r')

            # Press "g" for green
            elif key == ord('g'):
                color = (0, 255, 0)
                color_str = 'GREEN'
                print(Fore.GREEN + color_str + ' color selected.                                ' + Style.RESET_ALL,
                      end='\r')

            # Press "r" for red
            elif key == ord('r'):
                color = (0, 0, 255)
                color_str = 'RED'
                print(Fore.RED + color_str + ' color selected.                                      ' + Style.RESET_ALL,
                      end='\r')

            # Press "+" to increase pencil size
            elif key == ord('+'):
                size = size + 1
                print('Pencil size is now ' + Fore.GREEN + str(
                    size) + Style.RESET_ALL + '                               ', end='\r')

            # Press "-" to decrease pencil size
            elif key == ord('-'):
                size = size - 1
                if size < 0:
                    size = 0
                print(
                    'Pencil size is now ' + Fore.RED + str(size) + Style.RESET_ALL + '                              ',
                    end='\r')

            # Press "m" to paint with mouse
            elif key == ord('m'):
                mouse_painting = True
                print('You pressed "m". You are painting with the mouse.             ', end='\r')

            # Press "n" to paint with the mask
            elif key == ord('n'):
                mouse_painting = False
                print('You pressed "n". You are painting with the mask.                ', end='\r')

            # Press "v" to switch between showing real frame on canvas or a blank image
            elif key == ord('v'):

                real_frame = True

                if real_frame:

                    print('"v" was pressed. Real frame active on canvas', end='\r')

                else:

                    print('"v" was pressed. White image active on canvas', end='\r')

            # Press "c" to clear the window
            elif key == ord('c'):

                blank_image = 255 * np.ones(shape=[window_height, window_width, 3], dtype=np.uint8)
                print('\nYou pressed "c": The window "Canvas" was cleared.')

            # Press "w" to save the canvas image
            elif key == ord('w'):
                date = ctime()
                cv2.imwrite('drawing_' + date + '.png', blank_image)
                print('\nCurrent image saved as: ' + Fore.BLUE + 'drawing_' + date + '.png' + Style.RESET_ALL)

            # Press "s" to draw a rectangle
            if key == ord('s'):
                # If using mask mode
                if not mouse_painting and centroid is not None:
                    # If the previous pressed key was not s, create a cache and save the starting point
                    if listkeys[-2] != ord('s'):
                        cache = copy.deepcopy(blank_image)
                        start_point = (round(centroid[0]), round(centroid[1]))
                    else:
                        if cache is None:
                            cache = copy.deepcopy(blank_image)
                        if start_point is None:
                            start_point = (round(centroid[0]), round(centroid[1]))
                        end_point = (round(centroid[0]), round(centroid[1]))
                        blank_image = copy.deepcopy(cache)
                        cv2.rectangle(blank_image, start_point, end_point, color, size)

                # If used on "mouse" mode
                elif mouse_painting:
                    if center_mouse is not None:
                        if listmouse[-2] is None:
                            cache_mouse = copy.deepcopy(blank_image)
                            start_point_mouse = center_mouse
                        else:
                            if start_point_mouse is None:
                                start_point_mouse = center_mouse
                            if cache_mouse is None:
                                cache_mouse = copy.deepcopy(blank_image)
                            end_point_mouse = center_mouse
                            blank_image = copy.deepcopy(cache_mouse)
                            cv2.rectangle(blank_image, start_point_mouse, end_point_mouse, color, size)

            # Press "o" to draw a circle
            elif key == ord('o'):
                # If used on "mask" mode
                if not mouse_painting and centroid is not None:
                    # If the previous pressed key was not o, create a cache and save the starting point
                    if listkeys[-2] != ord('o'):
                        cache = copy.deepcopy(blank_image)
                        start_point = (round(centroid[0]), round(centroid[1]))
                    # If the previous pressed keys was an o, draw circle
                    else:
                        if cache is None:
                            cache = copy.deepcopy(blank_image)
                        if start_point is None:
                            start_point = (round(centroid[0]), round(centroid[1]))

                        end_point = (round(centroid[0]), round(centroid[1]))
                        radius = int(((start_point[0] - end_point[0]) ** 2 + (start_point[1] - end_point[1]) ** 2)
                                     ** (1 / 2))
                        blank_image = copy.deepcopy(cache)
                        cv2.circle(blank_image, start_point, radius, color, size)

                # If used on "mouse" mode
                elif mouse_painting:
                    if center_mouse is not None:
                        if listmouse[-2] is None:
                            cache_mouse = copy.deepcopy(blank_image)
                            start_point_mouse = center_mouse
                        else:
                            if start_point_mouse is None:
                                start_point_mouse = center_mouse
                            if cache_mouse is None:
                                cache_mouse = copy.deepcopy(blank_image)
                            end_point_mouse = center_mouse
                            radius = int(((start_point_mouse[0] - end_point_mouse[0]) ** 2 + (start_point_mouse[1] -
                                                                                              end_point_mouse[
                                                                                                  1]) ** 2) ** (1 / 2))
                            blank_image = copy.deepcopy(cache_mouse)
                            cv2.circle(blank_image, start_point_mouse, radius, color, size)

        # If the thickness of the pencil is zero the program doesn't draw
        if size == 0:
            pass
        else:
            # Painting with the mouse and not drawing rectangles or circles
            if ispressed and mouse_painting and not key == ord('s') and not key == ord('o'):
                cv2.line(blank_image, center_prev_mouse, center_mouse, color, size)
                # Defining the center_prev to use in the next cycle
                center_prev_mouse = center_mouse

            # Painting with the mask and not drawing rectangles or circles
            elif not mouse_painting and not key == ord('s') and not key == ord('o'):

                if centroid is None:
                    pass

                else:
                    # convert variable centroid to a tuple
                    center = (int(centroid[0]), int(centroid[1]))
                    # If on shake prevention
                    if shake_prevention:

                        # Calculate the distance between the centroid detected and the previous centroid
                        distance = math.sqrt(((center[0] - center_prev[0]) ** 2) + ((center[1] - center_prev[1]) ** 2))

                        # If the distance is above a certain limit
                        if distance > limit:
                            # Center_prev to use in the next cycle
                            center_prev = center
                        else:
                            # Paint a line
                            cv2.line(blank_image, center_prev, center, color, size)
                            # Draw the center on frame
                            cv2.line(frame, center_prev, center, color, size)
                            # center_prev to use in the next cycle
                            center_prev = center
                    else:
                        # Paint a line
                        cv2.line(blank_image, center_prev, center, color, size)
                        cv2.line(frame, center_prev, center, color, size)
                        # Center_prev to use in the next cycle
                        center_prev = center

        if args['use_numeric_painting']:

            # Press space bar, to shut down and print statistics
            if key & 0xFF == ord(' '):
                print(Fore.WHITE + '\nThese are your statistics:' + Style.RESET_ALL)
                mean_square_error = mse(painted_image, blank_image)
                similarity = ssim(painted_image, blank_image, multichannel=True)

                print('Error: ' + str(round(mean_square_error, 2)) + ' , Similarity: '
                      + str(round(similarity * 100, 2)) + ' %')
                if 0 <= similarity < 0.5:
                    print(Back.RED + 'You got less than 50%. Try again' + Style.RESET_ALL
                          )
                elif 0.5 <= similarity < 0.75:
                    print(Back.YELLOW + 'Nice painting' + Style.RESET_ALL
                          )
                elif 0.75 <= similarity <= 1.0:
                    print(Back.GREEN + 'Perfect!' + Style.RESET_ALL
                          )

                compare_images(painted_image, blank_image, "Canvas vs. Paint")

                cv2.waitKey(0)

                break
        # Press v to change between real frame and blank image on canvas
        if real_frame:
            # Replace blank image with the real frame
            new_frame = combine(blank_image, frame)
            # Show the real frame on canvas
            cv2.imshow("Canvas", new_frame)
        else:
            # Show the blank image on canvas
            cv2.imshow("Canvas", blank_image)

        cv2.imshow("Original", frame)
        cv2.imshow("Mask", mask_original)
        cv2.imshow("MaxArea", image_green)

        # Press "q" to shut down the program
        if key & 0xFF == ord('q'):
            print(Fore.RED + '\nYou closed the program.' + Style.RESET_ALL)
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
