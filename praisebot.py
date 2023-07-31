from pyautogui import *
import pyautogui
import time
import keyboard
import numpy as np
import random

# GLOBALS
training_menu = (130, 636)
indy_training_area = (1271, 162)
first_player_area = (1267, 405)
#top_right_praise_button = (3488, 261)
top_right_praise_button = (3505,255)
#praise_button = (1809, 1102)
praise_button = (1862, 1102)
#end_qc_top_right = (2690, 382)
end_qc_top_right = (2681, 388)
hover_duration = 0.1
players_to_praise = 25
y_iter = 89


# Define separate move and click functions
def my_move(coord_tuple):
    x, y = coord_tuple
    pyautogui.moveTo(x, y, duration=hover_duration)


def my_click():
    pyautogui.mouseDown()
    #time.sleep(0.1)
    pyautogui.mouseUp()

    
def orientate():
    # Training area setup
    time.sleep(5)

    # Navigate to Training Menu
    my_move(training_menu)
    my_click()

    # Click on Individual Training
    time.sleep(2)
    my_move(indy_training_area)
    my_click()


# To display mouse position
# pyautogui.displayMousePosition()


def my_praise_click():
    my_move(top_right_praise_button)
    my_click()
    # Click 1st praise choice
    my_move(praise_button)
    my_click()
    # End chat 
    my_move(end_qc_top_right)
    my_click()

    
def praise_button_exists(button):
    x, y = button
    return pyautogui.pixel(x, y) == (255,255,255)


def click_praise_buttons():
    my_move(top_right_praise_button)
    my_click()
    # Click 1st praise choice
    my_move(praise_button)
    my_click()
    # End chat 
    my_move(end_qc_top_right)
    my_click()


if __name__ == "__main__":
    # Provide time to move alt-tab to app
    time.sleep(7)
    # Go to Training>Indivdual menus
    orientate()

    # Set first position on first player and mouse click
    first_player_button = (1267, 385)
    my_move(first_player_button)
    my_click()
    
    for i in range(players_to_praise):
        if praise_button_exists(top_right_praise_button):
            print("Praise is there")
            #time.sleep(2)
            click_praise_buttons()
        pyautogui.press('down')
        #print(f"Iteration is {i}")
