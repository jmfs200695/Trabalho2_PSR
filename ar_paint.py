#!/usr/bin/python3

from functools import partial
from colorama import Fore, Back, Style
from my_functions import *
from termcolor import cprint
from time import ctime
import json
import argparse


def onMouse(event, x, y, flags, param):
    """
    Retrieving mouse coordinates while left button is clicked
    :param event:
    :param x:
    :param y:
    :return:
    """
    global ispressed
    global center_mouse

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
    global center_mouse, ispressed, cache, blank_original

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

    # Webcam video capture
    capture = cv2.VideoCapture(0)  # Camera 0 selected
    ret, frame = capture.read()

    ap = argparse.ArgumentParser(description='Paint on Augmented Reality')
    ap.add_argument('-j', '--json', required=True, help="Input json file path")
    ap.add_argument('-unp', '--numeric_paint', action='store_true',
                    help='Select this option to use numeric paint.')
    args = vars(ap.parse_args())

    with open(args['json']) as file_handle:
        # returns JSON object as a dictionary
        limits = json.load(file_handle)

    if args['numeric_paint']:
        # Print
        cprint('You chose numeric paint mode!'
               , color='white')

        # Generating the numeric picture
        blank_image, painted_image = drawNumericPaintImage(blank_image=blank_image, colour_list=colourlst)
        blank_original = copy.deepcopy(blank_image)

        # Print to the user which color should he print in it index
        print('\nColor index 1 corresponds to ' + Fore.RED + 'red ' + Fore.RESET + 'color.')
        print('Color index 4 corresponds to ' + Fore.GREEN + 'green ' + Fore.RESET + 'color.')
        print('Color index 5 corresponds to ' + Fore.BLUE + 'blue ' + Fore.RESET + 'color.')
        print("\nYou can also check the 'Painted image' to see how it should be like")
        print('Press the space bar to finish and evaluate your painting...\n')

        # Defining the window and showing the painted image
        cv2.namedWindow('Painted Image', cv2.WINDOW_NORMAL)
        cv2.imshow('Painted Image', painted_image)

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

    cv2.namedWindow('Canvas', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Original', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Mask', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('MaxArea', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Canvas', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Canvas', blank_image)

    # Defining mouse callback
    cv2.setMouseCallback("Canvas", onMouse)

    while capture.isOpened():
        # Get an image from the camera (a frame) and show it
        ret, frame = capture.read()
        frame = cv2.flip(frame, 1)

        # Create original mask
        mask_original = createMask(limits, frame)

        # Find centroid
        mask, centroid = getCentroid(mask_original)

        # Create a green mask for max area
        image_green = maxArea(frame, mask)

        listmouse.append(center_mouse)

        key = cv2.waitKey(1)  # Wait a key to stop the program

        # if a key is pressed
        if key != -1:

            # Choose the color blue if "b" is pressed.
            if key == ord('b'):
                color = (255, 0, 0)
                color_str = 'BLUE'
                print(Fore.BLUE + color_str + ' color selected.                                   ' + Style.RESET_ALL,
                      end='\r')

            # Choose the color green if "g" is pressed.
            elif key == ord('g'):
                color = (0, 255, 0)
                color_str = 'GREEN'
                print(Fore.GREEN + color_str + ' color selected.                                ' + Style.RESET_ALL,
                      end='\r')

            # Choose the color red if "r" is pressed.
            elif key == ord('r'):
                color = (0, 0, 255)
                color_str = 'RED'
                print(Fore.RED + color_str + ' color selected.                                      ' + Style.RESET_ALL,
                      end='\r')

            # Increase the pencil size if "+" is pressed.
            elif key == ord('+'):
                size = size + 1
                print('Pencil size is now ' + Fore.GREEN + str(
                    size) + Style.RESET_ALL + '                               ', end='\r')

            # Decrease the pencil size if "-" is pressed.
            elif key == ord('-'):
                size = size - 1
                if size < 0:
                    size = 0
                print(
                    'Pencil size is now ' + Fore.RED + str(size) + Style.RESET_ALL + '                              ',
                    end='\r')

            # Paint with the mouse if "m" is pressed.
            elif key == ord('m'):
                mouse_painting = True
                print('You pressed "m". You are painting with the mouse.             ', end='\r')

            # Paint with the mask if "n" is pressed.
            elif key == ord('n'):
                mouse_painting = False
                print('You pressed "n". You are painting with the mask.                ', end='\r')

            # Clear the window if "c" is pressed.
            elif key == ord('c'):

                blank_image = 255 * np.ones(shape=[window_height, window_width, 3], dtype=np.uint8)
                print('\nYou pressed "c": The window "Canvas" was cleared.')

            # Save the current image if "w" is pressed.
            elif key == ord('w'):
                date = ctime()
                cv2.imwrite('drawing_' + date + '.png', blank_image)
                print('\nCurrent image saved as: ' + Fore.BLUE + 'drawing_' + date + '.png' + Style.RESET_ALL)

            # Draw a rectangle when pressing 's' key
            if key == ord('s'):
                # on "mask" mode
                if not mouse_painting and centroid is not None:
                    # If the previous pressed key was not s, create a cache and save the starting point
                    if listkeys[-2] != ord('s'):
                        cache = copy.deepcopy(blank_image)
                        start_point = (round(centroid[0]), round(centroid[1]))

                    # If the previous pressed key was an s, draw rectangle
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

            # Draw a circle when pressing 'o' key
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

        if size == 0:
            pass
        else:
            # Painting with the mouse, not drawing rectangles or circles
            if ispressed and mouse_painting and not key == ord('s') and not key == ord('o'):
                cv2.line(blank_image, center_prev_mouse, center_mouse, color, size)
                # Defining the center_prev to use in the next cycle
                center_prev_mouse = center_mouse

            # Painting with the mask, not drawing rectangles or circles
            elif not mouse_painting and not key == ord('s') and not key == ord('o'):

                if centroid is None:
                    pass

                else:
                    # Change the variable centroid to a tuple
                    center = (int(centroid[0]), int(centroid[1]))
                    cache = copy.deepcopy(blank_image)
                    blank_image = copy.deepcopy(cache)
                    start_point = (round(centroid[0]), round(centroid[1]))

                    # Paint a line according to the inputs
                    cv2.line(blank_image, center_prev, start_point, color, size)
                    cv2.line(frame, center_prev, center, color, 4)
                    # Defining the center_prev to use in the next cycle
                    center_prev = center

        cv2.imshow('Canvas', blank_image)
        cv2.imshow("Original", frame)
        cv2.imshow("Mask", mask_original)
        cv2.imshow("MaxArea", image_green)

        # If you press q, the program shuts down
        if key & 0xFF == ord('q'):
            print(Fore.RED + '\nThe program closed.' + Style.RESET_ALL)
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
