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

# Load the defensive player image and ensure it is in the correct format
defensive_player_image_path = 'orange_down_arrow_chat.png'
defensive_player_image = cv2.imread(defensive_player_image_path, cv2.IMREAD_COLOR)


# Verify that the reference image is loaded properly
if reference_image is None:
    raise ValueError("Reference image not found or unable to load.")
    
# Verify that the defensive player image is loaded properly
if defensive_player_image is None:
    raise ValueError("Defensive player image not found or unable to load.")

def define_region(bottom_right, top_left):
    bottom_right_x, bottom_right_y = bottom_right
    top_left_x, top_left_y = top_left
    return (top_left_x, top_left_y,
            (bottom_right_x - top_left_x),
            (bottom_right_y - top_left_y))

    
# Define the Rating region of the screen to capture (x, y, width, height)
RATING_REGION_BOT_RIGHT = (1189, 2122)
RATING_REGION_TOP_LEFT = (1076, 412)

RATING_REGION = define_region(RATING_REGION_BOT_RIGHT, RATING_REGION_TOP_LEFT)


# Define region of screen where player's face and info appears in Quick Chat
PLAYER_CHAT_BOT_RIGHT= (1376, 1511)
PLAYER_CHAT_TOP_LEFT = (958, 375)

PLAYER_CHAT_REGION = define_region(PLAYER_CHAT_BOT_RIGHT, PLAYER_CHAT_TOP_LEFT)

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


# Back down button in the pop-up dialog.
# These can vary based on size of response window.
MODAL_BACK_DOWN_BUTTON_1 = (1516, 833)
MODAL_BACK_DOWN_BUTTON_2 = (1516, 1033)


# End the quick chat in modal pop-up
END_QC_BUTTON = (2759, 317)


# We need to "scroll down" to find more players if we have good 
# rating players below the fold. We click in the right gutter area
SCROLL_DOWN_GUTTER = (1218, 2064)

# We need to "scroll down" to find more players if we have good 
# rating players below the fold. We click in the right gutter area
SCROLL_UP_GUTTER = (1218, 417)


# Set up "defensive" player color and position. The color _may_ change
# maybe? Not sure if configurable. The "color bar" is the bar that 
# displays player body language. We choose the section that has not text
# to prevent this from misfiring.

# Set up "defensive" player color and position
DEFENSIVE_COLOR = (153, 147, 87)
DEFENSIVE_PLAYER_COLOR_BAR = (1237, 717)


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
    
    # Click first player
    my_move(TOP_PLAYER_AREA)
    my_click()

def player_is_defensive(player_chat_region, reference_image=reference_image, defensive_player_image=defensive_player_image):
	# Take a screenshot of the specified player chat region
    screenshot = pyautogui.screenshot(region=player_chat_region)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Ensure both images are of the same type (either both grayscale or both color)
    # If using grayscale, uncomment the following lines:
    # reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    # screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)    

    # Find the reference image within the screenshot
    result = cv2.matchTemplate(screenshot, defensive_player_image, cv2.TM_CCOEFF_NORMED)

    # Set a threshold for the maximum score
    threshold = 0.9

    # Find the maximum score and its location
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Check if the maximum score is above the threshold
    if max_val > threshold:
        print('Template image found at location:', max_loc)
        return True
    else:
        print('Template image not found')
        return None
    
    
    
    
# To display mouse position
# pyautogui.displayMousePosition()


def my_praise_click():
    my_move(TOP_RIGHT_PRAISE_BUTTON)
    my_click()
    # Click 1st praise choice
    my_move(MODAL_PRAISE_BUTTON)
    my_click()
	# If player gets defensive, we should see an orange-ey down arrow in certain region.
	# We should back down after a praise attempt, and the remaining logic should stand.
    if player_is_defensive(PLAYER_CHAT_REGION):
        print("We have found a defensive player")
        my_move(MODAL_BACK_DOWN_BUTTON_1)
        my_click()
        time.sleep(2)
        my_move(MODAL_BACK_DOWN_BUTTON_2)
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

def click_ratings(rating_region):
	
    # Take a screenshot of the specified rating_region
    screenshot = pyautogui.screenshot(region=rating_region)
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
    #pprint.pprint(locations)
    
    # Process each matching location
    i = 0
    for loc in grouped_locations:
        # Calculate the center point
        center_x = loc[0] + int(reference_image.shape[1] / 2)
        center_y = loc[1] + int(reference_image.shape[0] / 2)

        # Add the rating_region's offset to get the absolute screen position
        screen_x = rating_region[0] + center_x
        screen_y = rating_region[1] + center_y

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

	
	
if __name__ == "__main__":
    # Provide time to move alt-tab to app
    time.sleep(2)
    # Go to Training>Indivdual menus
    orientate()

    my_move(SCROLL_UP_GUTTER)
    my_click()
    click_ratings(RATING_REGION)
    my_move(SCROLL_DOWN_GUTTER)
    my_click()
    click_ratings(RATING_REGION)
    my_move(SCROLL_UP_GUTTER)
    my_click()
