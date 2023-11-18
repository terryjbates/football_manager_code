from pyautogui import *
import cv2
import pyautogui
import time
import keyboard
import numpy as np
import random
import pprint

def group_locations(locations, threshold=10):
    """
    Group nearby locations to treat them as a single location.
    """
    grouped = []
    for loc in locations:
        if not grouped:
            grouped.append([loc])
        else:
            match = False
            for group in grouped:
                if abs(group[0][0] - loc[0]) < threshold and abs(group[0][1] - loc[1]) < threshold:
                    group.append(loc)
                    match = True
                    break
            if not match:
                grouped.append([loc])
    return [tuple(np.mean(g, axis=0).astype(int)) for g in grouped]


# Load the reference image and ensure it is in the correct format
reference_image_path = 'green_space_near_player.png'
reference_image = cv2.imread(reference_image_path, cv2.IMREAD_COLOR)

# Verify that the reference image is loaded properly
if reference_image is None:
    raise ValueError("Reference image not found or unable to load.")

# Define the region of the screen to capture (x, y, width, height)
region_bot_right_x, region_bot_right_y = (1189, 2055) 
region = (1076, 412, (region_bot_right_x - 1076), (region_bot_right_y - 412))

# GLOBALS
HOVER_DURATION = 0.2
# Bookmark link in bottom left 
INDY_TRAINING_AREA = (1387, 179)
# Location of first player row top left
TOP_PLAYER_AREA = (1267, 405)

# Roughly equivalent to number of players that 
# have > 7.0 scores in total. 
PLAYERS_TO_PRAISE = 17  # Start with 17 and see how far we get

# Top right praise button, white rectangle top right
# We aim for the white baloon
TOP_RIGHT_PRAISE_BUTTON = (3474,284)

# Praise button in the pop-up dialog after hitting
# top right praise button
MODAL_PRAISE_BUTTON = (1597, 1018)

# End the quick chat in modal pop-up
END_QC_BUTTON = (2759, 317)


# Define separate move and click functions
def my_move(coord_tuple):
    x, y = coord_tuple
    pyautogui.moveTo(x, y, duration=HOVER_DURATION)


def my_click():
    pyautogui.mouseDown()
    #time.sleep(0.1)
    pyautogui.mouseUp()

    
def orientate():
    # Training area setup
    time.sleep(5)

    # Navigate to Training Menu using FM shortcut
    pyautogui.hotkey('ctrl', 'r')
    time.sleep(1)

    # Click on Individual Training
    time.sleep(2)
    my_move(INDY_TRAINING_AREA)
    my_click()


# To display mouse position
# pyautogui.displayMousePosition()


def my_praise_click():
    my_move(TOP_RIGHT_PRAISE_BUTTON)
    my_click()
    # Click 1st praise choice
    my_move(MODAL_PRAISE_BUTTON)
    my_click()
    # End chat 
    my_move(END_QC_BUTTON)
    my_click()

    
def praise_button_exists(button):
    x, y = button
    return pyautogui.pixel(x, y) == (255,255,255)


def click_praise_buttons():
    my_move(TOP_RIGHT_PRAISE_BUTTON)
    my_click()
    # Click 1st praise choice
    my_move(MODAL_PRAISE_BUTTON)
    my_click()
    # End chat 
    my_move(END_QC_BUTTON)
    my_click()


if __name__ == "__main__":
    # Provide time to move alt-tab to app
    time.sleep(2)
    # Go to Training>Indivdual menus
    orientate()

    # Set first position on first player and mouse click
    # first_player_button = (1267, 385)
    my_move(TOP_PLAYER_AREA)
    my_click()

    # Take a screenshot of the specified region
    screenshot = pyautogui.screenshot(region=region)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Ensure both images are of the same type (either both grayscale or both color)
    # If using grayscale, uncomment the following lines:
    # reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    # screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)    

    # Find the reference image within the screenshot
    result = cv2.matchTemplate(screenshot, reference_image, cv2.TM_CCOEFF_NORMED)


    # Define a threshold
    threshold = 0.80

    # Get the locations where the matches exceed the threshold
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    # Group the locations
    grouped_locations = group_locations(locations)
    
    # Pretty print locations detected
    pprint.pprint(locations)
    
    # Process each matching location
    i = 0
    for loc in grouped_locations:
        # Calculate the center point
        center_x = loc[0] + int(reference_image.shape[1] / 2)
        center_y = loc[1] + int(reference_image.shape[0] / 2)

        # Add the region's offset to get the absolute screen position
        screen_x = region[0] + center_x
        screen_y = region[1] + center_y

        # Perform the click and praise action
        pyautogui.click(screen_x, screen_y)
        print(f"Clicked {screen_x}, {screen_y} and now sleeping" )
        time.sleep(0.5)  # Adjust sleep time as needed
        # Add your 'praise player' code here
        if praise_button_exists(TOP_RIGHT_PRAISE_BUTTON):
            my_praise_click()
        # Diagnostic code in case we need to bug fix
        #i += 1
        #if i > 5:
        #    break
        # Optionally, add a small delay between processing each location
        time.sleep(0.2)
