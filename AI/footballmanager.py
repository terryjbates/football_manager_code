import os
import io
import time
import pyautogui
from pywinauto.application import Application
import pytesseract
import re
from datetime import datetime
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import janitor

from fuzzywuzzy import process, fuzz
from bs4 import BeautifulSoup
from IPython.display import display, HTML
from mss import mss
from PIL import Image

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt
import seaborn as sns

import codecs


import typing
# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Globals

# Set a sleep duration to allow for navigation
SLEEP_DURATION = 2

# Number of teams
num_of_teams = 18

# Define screen resolution
screen_width, screen_height = 3840, 2160

# Define text pattern for the team that we manage
PLAYER_TEAM_PATTERN = ".*Aduana.*"

# Club-Specific data
CLUB_SPECIFIC_DATA = "Ghanian Premier League Data - Sheet1.csv"

# Example coordinates for specific areas (adjust these to match your actual screen)
menu_cup_icon_coords = (49, 937)  # Example coordinates for "cup" icon
zylofon_league_coords = (476, 317)  # Coordinates for Zylofon League
matches_results_coords = (1271, 329)  # Coordinates for "MATCHES/RESULTS>"
first_league_team_coords = (444, 564) # Coords for first team in league screen
team_schedule_coords = (1167, 170) # Coordinates for "Schedule" on a team page
back_button_coords = (152, 69) # Back button coords
match_view_1_coords = (406, 245) # Back button coords
match_view_2_coords = (406, 323)
match_view_3_coords = (787, 80) # Back button coords
print_ok_coords = (2109, 1239) # Print "OK" button coords
data_dumps_coords = (1547, 1020) # Data_dumps dir file dir (may change)
league_team_offset = 53


# Coordinates for the region where dates appear on the screen (adjust these)
# date_region = (2510, 225, 793, 58)  # Example coordinates (x, y, width, height)
date_region = (3199, 41, 205, 71)
# Coordinates for the region where dates appear on the screen (adjust these)
team_name_region = (555, 29, 1119, 46)  # Example coordinates (x, y, width, height)


BASE_DIR = r"C:\Users\lover\OneDrive\Documents\GitHub\football_manager_code\AI\Match_Data_Capture"
DATA_DIR = r"C:\Users\lover\OneDrive\Documents\Sports Interactive\Football Manager 2024\data_dumps"

# Functions

# Function to navigate to Football Manager 2024 Window
def navigate_to_fm_window(window_title="Football Manager 2024"):
    time.sleep(SLEEP_DURATION)
    try:
        app = Application().connect(title_re=window_title)
        app.top_window().set_focus()
        print(f"{window_title} window is now active.")
    except Exception as e:
        print(f"Failed to activate {window_title} window: {e}")

        
# Create generic navigation function
def click_on_coords(coords):
    pyautogui.click(coords)
    time.sleep(SLEEP_DURATION)


# Click on the "cup" icon to go to the Competitions screen
def navigate_to_competitions():
    pyautogui.click(menu_cup_icon_coords)
    time.sleep(SLEEP_DURATION)

	
# Click on the "Zylofon Cash Premier League" link
def navigate_to_zylofon_league():
    pyautogui.click(zylofon_league_coords)
    time.sleep(SLEEP_DURATION)


# Click on the "MATCHES/RESULTS>" link
def click_matches_results():
    pyautogui.click(matches_results_coords)
    time.sleep(SLEEP_DURATION)


# Click on the "MATCHES/RESULTS>" link
def click_team_schedule():
    pyautogui.click(team_schedule_coords)
    time.sleep(SLEEP_DURATION)


def navigate_to_league_team(offset_count=0):
    x, y = first_league_team_coords
    # print(f"Offset Count:{offset_count} , Offset{league_team_offset}")
    y = y + (offset_count * league_team_offset)
    # print(f"Moving to x:{x} y:{y}")
    
    # pyautogui.click(x, y)
    # time.sleep(SLEEP_DURATION)
    click_on_coords((x,y))

	
# Navigate to our custom match view
def navigate_to_custom_matches_view():
    # pyautogui.click(match_view_1_coords)
    # time.sleep(SLEEP_DURATION)
    # pyautogui.click(match_view_2_coords)
    # time.sleep(SLEEP_DURATION)
    click_on_coords(match_view_1_coords)
    click_on_coords(match_view_2_coords)
    click_on_coords(match_view_3_coords)


# Navigate to our custom match view
def navigate_to_player_schedule():
    pyautogui.press('f10')
    time.sleep(SLEEP_DURATION)


def back_button():
    pyautogui.click(back_button_coords)
    time.sleep(SLEEP_DURATION)


# Example function to capture screen using OpenCV and mss
def capture_screen_with_mss(region=None, save_path="current_screen.png"):
    with mss() as sct:
        # If a region is defined, capture only that part of the screen
        if region:
            monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
        else:
            # Capture the full screen
            monitor = sct.monitors[1]

        # Capture the screenshot
        screenshot = sct.grab(monitor)

        # Convert the screenshot to a numpy array (BGRA format)
        img = np.array(screenshot)

        # Convert from BGRA to BGR (remove the alpha channel)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Save the screenshot as a PNG file
        cv2.imwrite(save_path, img_bgr)
    

def capture_and_process_date(region=None):
    # Capture the screen region
    screenshot = pyautogui.screenshot(region=region)
    
    # Save the screenshot for debugging
    screenshot.save("date_region.png")
    
    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(screenshot)
    print(f"Extracted date text: {text}")
    
    # Return the extracted text for further processing
    return text


# Function to capture and process the date region using OpenCV and pytesseract
def capture_and_process_date_with_mss(region):
    # Capture the date region using mss
    capture_screen_with_mss(region=region, save_path="date_region.png")

    # Load the captured image
    img = cv2.imread("date_region.png")

    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(img)
    print(f"Extracted date text: {text}")

    return text


# Preprocess the image for better OCR accuracy using OpenCV
def preprocess_image_for_ocr(image):
    # Convert to grayscale
    gray_img = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to enhance contrast
    processed_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
    return processed_img


def capture_and_process_screen(region=None):
    # Capture the screen (or specific region)
    screenshot = pyautogui.screenshot(region=region)
    
    # Convert the screenshot to OpenCV format and preprocess
    processed_img = preprocess_image_for_ocr(screenshot)
    
    # Convert processed image back to PIL format for pytesseract
    pil_img = Image.fromarray(processed_img)
    
    # Use pytesseract to extract text from the preprocessed image
    text = pytesseract.image_to_string(pil_img)
    
    # Debugging: Save the processed image
    pil_img.save("processed_screen.png")
    
    print(f"Extracted text: {text}")
    return text


# Function to capture and process the date region using OpenCV and pytesseract
def capture_and_process_team_name(region=team_name_region):
    # Capture the date region using mss
    capture_screen_with_mss(region=region, save_path="team_name_region.png")
    extracted_text = extract_text_from_image("team_name_region.png")
    # print(f"Extracted Text: {extracted_text}")
    time.sleep(SLEEP_DURATION)
    return extracted_text



def extract_text_from_image(image_path):
    # Load the image using OpenCV or PIL
    image = cv2.imread(image_path)
    
    # Preprocess the image for better OCR results (convert to grayscale)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to extract text
    extracted_text = pytesseract.image_to_string(gray_image)
    
    return extracted_text    


# Parse the extracted date and time text
def parse_date(text):
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    cleaned_text =  re.sub(r'\n', ' ', cleaned_text).strip()
    try:
        time_obj = datetime.strptime(cleaned_text, "%a %H:%M %d %b %Y")
        return (time_obj.strftime("%Y_%m_%d"))
    except ValueError as e:
        print(f"Failed to parse date: {e}")
        return None


def extract_text_from_image(image_path):
    # Load the image using OpenCV or PIL
    image = cv2.imread(image_path)
    
    # Preprocess the image for better OCR results (convert to grayscale)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to extract text
    extracted_text = pytesseract.image_to_string(gray_image)
    
    return extracted_text    


def select_all_matches():

    pyautogui.press('pageup')
    pyautogui.press('pageup')
    time.sleep(SLEEP_DURATION)
    print("Paged Up")
    print_mouse_position()

    click_reference_image("./First_Match_Date.png")
    time.sleep(SLEEP_DURATION)

    # Select all matches
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(SLEEP_DURATION)
    pyautogui.hotkey('ctrl', 'p')


def print_match_data_to_file(output_file):

    # Select all matches
    select_all_matches()
    
    # Click OK on output dialog
    click_on_coords(print_ok_coords)
    time.sleep(SLEEP_DURATION)

    double_click_data_dumps()
    time.sleep(SLEEP_DURATION)
    
    # Click on the coords for "Save As"
    click_on_coords((1852, 682))
    time.sleep(SLEEP_DURATION)
    
    # Double click in the field to highlight all text
    pyautogui.doubleClick()
    
    # Enter the file name
    pyautogui.write(output_file)
    time.sleep(SLEEP_DURATION)
    
    # Hit <enter> to OK the save file
    pyautogui.press('enter')
    time.sleep(SLEEP_DURATION)


def parse_html_table(file_path):
    #with open(file_path, 'r') as f:
    with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table')  # Adjust the selector if needed

    # Find headers and data rows directly from the table
    headers = [th.text for th in table.find_all('th')]
    data = []
    for row in table.find_all('tr')[1:]:  # Skip the first row if it's a header
        row_data = [td.text for td in row.find_all('td')]
        data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    return df


# Define a function that attempts to convert a column to numeric
def convert_to_numeric(df, column):
    try:
        # Convert to numeric
        df[column.name] = pd.to_numeric(column.str.replace(',',''), errors='coerce')  # Convert non-numeric to NaN
        # df[column] = pd.to_numeric(df[column].str.replace(',', ''), errors='coerce')  # Convert non-numeric to NaN
        print(f"Converted {column.name} to numeric")
    except Exception as e:
        print(f"Error processing {column.name}: {e}")
		

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


def double_click_data_dumps():
    reference_image_path = './data_dump_folder.png'
    # Load the reference image and ensure it is in the correct format
    reference_image = cv2.imread(reference_image_path, cv2.IMREAD_COLOR)

    # Verify that the reference image is loaded properly
    if reference_image is None:
        raise ValueError("Reference image not found or unable to load.")

    # Take a screenshot of the specified rating_region
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Ensure both images are of the same type (either both grayscale or both color)
    # If using grayscale, uncomment the following lines:
    reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)    

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

        # # Add the rating_region's offset to get the absolute screen position
        # screen_x = rating_region[0] + center_x
        # screen_y = rating_region[1] + center_y

        # Perform the click and praise action
        #pyautogui.click(screen_x, screen_y)
        print(f"Want to click on data_dumps at {center_x}, {center_y}" )
        click_on_coords((center_x, center_y))
        pyautogui.doubleClick()


def open_dir(dir_name):
    os.chdir(dir_name)
    os.getcwd()
# os.chdir(DATA_DIR)
# os.getcwd()

# Execute data capture code    
# Example usage of the navigation and screen capture functions
def generate_match_data_files():
    time.sleep(5)
    # Step 0: Navigate to FM
    navigate_to_fm_window()
    
    # Hit escape if needed
    pyautogui.press('esc')
    # Step 1: Navigate to the Competitions screen
    # navigate_to_competitions()
    click_on_coords(menu_cup_icon_coords)

    # Step 2: Navigate to the Zylofon Cash Premier League
    # navigate_to_zylofon_league()
    click_on_coords(zylofon_league_coords)
    
    # Step 3: We want to iterate over every team, so we need to calculate 
    # the size of the region with teams, divide by the number of teams
    # in the league.
    for i in range(num_of_teams):
        navigate_to_league_team(i)
        # navigate_to_zylofon_league()
        # click_team_schedule()
        # back_button()
        team_name = capture_and_process_team_name()
        print(f"Team Name: {team_name}")
        if re.search(PLAYER_TEAM_PATTERN, team_name):
            navigate_to_player_schedule()
        else:
            # click_team_schedule()
            click_on_coords(team_schedule_coords)

        navigate_to_custom_matches_view()
        date_text = capture_and_process_date_with_mss(region=date_region)
        parsed_date = parse_date(date_text)
        # Save our match data to file via CTRL-A, CTRL-P + use Team Name
        output_file_name = parsed_date + "_"  + team_name
        print(f"Output File: {output_file_name}")
        print_match_data_to_file(output_file_name)

        back_button()
        back_button()



def extract_team_names(file_list):
    team_names = []
    for file_name in file_list:
        # Split by underscores
        parts = file_name.split('_')
        
        # Get the last part (team name with .html extension)
        team_name_with_extension = parts[-1]
        
        # Remove the .html extension
        team_name = os.path.splitext(team_name_with_extension)[0]
        
        # Add the team name to the list
        team_names.append(team_name)
    
    return team_names


def extract_single_team_name(file_name):
    # Split by underscores
    parts = file_name.split('_')
    # Get the last part (team name with .html extension)
    team_name_with_extension = parts[-1]

    # Remove the .html extension
    team_name = os.path.splitext(team_name_with_extension)[0]

    return team_name


def determine_venue(row):
    team_name = row['team']
    home_team = row['home_team']
    away_team = row['away_team']
    home_match = process.extractOne(team_name, [home_team])[1]
    away_match = process.extractOne(team_name, [away_team])[1]
    
    if home_match > away_match:
        return 'home'
    elif away_match > home_match:
        return 'away'
    else:
        return 'unknown' # Where fuzzy matching is incomplete


def determine_opponent(row):
    team_name = row['team']
    home_team = row['home_team']
    away_team = row['away_team']
    home_match = process.extractOne(team_name, [home_team])[1]
    away_match = process.extractOne(team_name, [away_team])[1]
    
    if home_match > away_match:
        return row['away_team']
    elif away_match > home_match:
        return row['home_team']
    else:
        return 'unknown' # Where fuzzy matching is incomplete

	
# def parse_html_table(file_path):
#     with open(file_path, 'r') as f:
#         soup = BeautifulSoup(f, 'html.parser')

#     table = soup.find('table')  # Adjust the selector if needed

#     # Find headers and data rows directly from the table
#     headers = [th.text for th in table.find_all('th')]
#     data = []
#     for row in table.find_all('tr')[1:]:  # Skip the first row if it's a header
#         row_data = [td.text for td in row.find_all('td')]
#         data.append(row_data)

#     # Create DataFrame
#     df = pd.DataFrame(data, columns=headers)
#     return df


def determine_text_result(row):
    initial_result = row['result']
    try:
        home, away = initial_result.strip(" ").split("-")
        home = int(home)
        away = int(away)

        # Determine textual result
        result = "D" if home == away else (
            "W" if (row['venue'] == 'home' and home > away) or (row['venue'] == 'away' and away > home) else "L"
        )
        return result
    except ValueError:
        # print(f"Length of result col: {len(initial_result)}")
        return None

	
def determine_goal_differential(row, flag='for'):
    initial_result = row['result']
    # print(f"Type of row['result']: {type(row['result'])}")
    # print(f"Result: {initial_result}")
    try:
        home, away = initial_result.strip(" ").split("-")
        home = int(home)
        away = int(away)
        
        score_map = {'home': { 'for': home, 'against': away },
                     'away': { 'for': away, 'against': home }}

        return score_map[row['venue']][flag]
    except (ValueError, TypeError) as e:
        print(f"Error processing result for row {row['index']}: {e}")
        return None

	
def imperial_to_decimal_height(height: str) -> float:
    # Check if the height is a valid string and in the correct format
    if isinstance(height, str) and "'" in height and '"' in height:
        try:
            # Split into feet and inches
            feet, inches = height.split("'")
            feet = int(feet)
            inches = int(inches.replace('"', ''))
        except (ValueError, KeyError):
            # Return NaN if the height format is invalid
            return np.nan

        # Convert to decimal format
        return round(feet + inches / 12, 2)
    
    # Return NaN if the value is not a valid string or doesn't match the format
    return np.nan


# def imperial_to_decimal_height(height):
#     # Check if the height is a valid string and in the correct format
#     if isinstance(height, str) and "'" in height and '"' in height:
#         try:
#             # Split into feet and inches
#             feet, inches = height.split("'")
#             feet = int(feet)
#             inches = int(inches.replace('"', ''))
#         except ValueError:
#             # Return NaN if the height format is invalid
#             return np.nan

#         # Convert to decimal format
#         return round(feet + inches / 12, 2)
    
#     # Return NaN if the value is not a valid string or doesn't match the format
#     return np.nan



def weight_to_decimal_weight(weight: str) -> float:
    # Check if the height is a valid string and in the correct format
    if isinstance(weight, str) and "lbs" in weight:
        try:
            # Split into feet and inches
            weight, lbs_str = weight.split(" ")
            weight = int(weight)
        except (ValueError, KeyError):
            # Return NaN if the height format is invalid
            return np.nan

        # Convert to decimal format
        return round(weight)
    
    # Return NaN if the value is not a valid string or doesn't match the format
    return np.nan


def convert_percent_string_to_decimal(row, col):
    percent_string = row[col]
    try:
        percent_string = percent_string.split("%")[0]
        percent_int = int(percent_string)
        percent_value = percent_int / 100
        return percent_value
    except (ValueError, TypeError) as e:
        print(f"Error processing result for row {row[col]}: {e}")
        return None

# scouting_df['Conv %'] = scouting_df.apply(lambda row: convert_percent_string_to_decimal(row, 'Conv %'), axis=1)


def determine_expires_date(row):
    initial_date = row['Expires']
    try:
        return datetime.strptime(initial_date, "%m/%d/%Y")
    except:
        return None
    
# lambda x: datetime.strptime(x, "%m/%d/%Y")


