import requests
import pandas as pd
import time
import re

# ==========================================
# 1. CONFIGURATION
# ==========================================
FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSeApSvFONQOQAl2wCEL_lTK4zuDEKq_mHtcoTL6qUHu1FeA4w/formResponse"

FORM_MAPPING = {
    'What is your age?': 'entry.1191115588',
    'What is your occupation?': 'entry.1307314062',
    'What is your marital status?': 'entry.1181595107',
    'Do you have any of these?': 'entry.1852588942',
    'Are your menstrual cycles regular and What is the average length of your menstrual cycle (in days)?': 'entry.244811129',
    'Do you experience pain or cramps during menstruation?': 'entry.821048846',
    'Do you ever miss your periods for more than two months (without pregnancy)?': 'entry.1726981697',
    'Do you experience excessive or very light bleeding?': 'entry.1634692932',
    'How often do you usually skip meals in a day?': 'entry.1240591276',
    'Do you take meals exactly on time?': 'entry.1815738368',
    'How often do you consume fast food or street food in a week?': 'entry.82247759',
    'Do you consume sugary or carbonated drinks regularly?': 'entry.474334067',
    'How often do you eat green leafy vegetables and fruits per week?': 'entry.1074686896',
    'Do you take any dietary supplements (e.g., iron, multivitamins)? If yes which one?': 'entry.598601211',
    'Do you believe that food habits, stress or poor diet can cause irregular periods and why?': 'entry.2070363150',
    'Are you aware of the importance of iron and calcium-rich foods during menstruation?': 'entry.1431550299',
    'Have you ever been informed (by doctor, teacher, or media) about the link between diet and menstrual health?': 'entry.1799813900',
    'Would you be willing to change your diet if you knew it would improve menstrual regularity and reduce pain?': 'entry.477219094'
}

CHECKBOX_COLUMNS = ['Do you have any of these?']

# ==========================================
# 2. THE GOLDEN LIST (Valid Options from HTML)
# ==========================================
# The script will look for these EXACT strings.
VALID_OPTIONS = {
    'What is your occupation?': ["Student", "Housewife", "Job-holder"],
    'What is your marital status?': ["Married", "Unmarried"],
    'Do you have any of these?': ["PCOS", "Pregnancy", "Thyroid", "Under hormonal therapy", "Endocrine disease",
                                  "None"],
    'Are your menstrual cycles regular and What is the average length of your menstrual cycle (in days)?': [
        "Regular- 21-24 days (short cycle)",
        "Regular- 25-28 days (Average cycle)",
        "Irregular – Less than 21 days",
        "Irregular- More than 35 days"
    ],
    'Do you experience pain or cramps during menstruation?': ["Yes", "No"],
    'Do you ever miss your periods for more than two months (without pregnancy)?': ["Yes", "No"],
    'Do you experience excessive or very light bleeding?': ["Normal", "Excessive", "Very Light Bleeding"],
    'How often do you usually skip meals in a day?': [
        "Never (I eat all meals daily)",
        "Rarely (1–2 times per week)",
        "Sometimes (3–4 times per week)",
        "Often (5–6 times per week)",
        "Every day (I skip at least one meal daily)",
        "Depends / Not consistent"
    ],
    'Do you take meals exactly on time?': ["Yes", "Sometimes", "No"],
    'How often do you consume fast food or street food in a week?': [
        "Everyday", "1-2 times per week", "3-4 times per week", "5-6 times", "Never"
    ],
    'Do you consume sugary or carbonated drinks regularly?': [
        "Everyday", "1-2 times per week", "3-4 times per week", "5-6 times", "Never"
    ],
    'How often do you eat green leafy vegetables and fruits per week?': [
        "Everyday", "1-2 times per week", "3-4 times per week", "5-6 times", "Never"
    ],
    'Are you aware of the importance of iron and calcium-rich foods during menstruation?': ["Yes", "No"],
    'Have you ever been informed (by doctor, teacher, or media) about the link between diet and menstrual health?': [
        "Yes", "No"],
    'Would you be willing to change your diet if you knew it would improve menstrual regularity and reduce pain?': [
        "Yes", "No"]
}


# ==========================================
# 3. FUZZY MATCH LOGIC
# ==========================================
def get_clean_string(s):
    """Removes all non-alphanumeric characters and makes lowercase"""
    return re.sub(r'[^a-zA-Z0-9]', '', str(s).lower())


def find_correct_option(col_name, csv_value):
    """
    Compares the CSV value against the VALID_OPTIONS list.
    Returns the exact string Google wants.
    """
    # If this column isn't a multiple choice question (like 'Age'), just return the text
    if col_name not in VALID_OPTIONS:
        return str(csv_value).strip()

    clean_csv = get_clean_string(csv_value)

    # Check against all valid options
    for option in VALID_OPTIONS[col_name]:
        if clean_csv == get_clean_string(option):
            return option  # RETURN THE GOLDEN STRING

    # If no match found, return original (it might fail, but we tried)
    # print(f"   [Warning] No match found for '{csv_value}' in '{col_name}'")
    return str(csv_value).strip()


# ==========================================
# 4. SUBMISSION LOOP
# ==========================================
try:
    df = pd.read_csv('F:\Data Science Journey\DataScienceRoadMap\practice_code\Thisis_Data_JU_heet1.csv', sep=',')
    df = df.fillna("")
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df)} rows.")
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit()

print("Starting submission...")
success_count = 0
fail_count = 0

for index, row in df.iterrows():
    submission_data = {}

    # Add Page History (Helps with multi-page form validation)
    submission_data['pageHistory'] = '0'

    for col_header, entry_id in FORM_MAPPING.items():
        if col_header in df.columns:
            raw_value = row[col_header]

            # --- Checkbox Handling ---
            if col_header in CHECKBOX_COLUMNS:
                if not raw_value:
                    submission_data[entry_id] = []
                else:
                    # Split CSV by comma, then find the Correct Option for each item
                    raw_items = str(raw_value).split(',')
                    clean_items = []
                    for item in raw_items:
                        correct_val = find_correct_option(col_header, item)
                        clean_items.append(correct_val)
                    submission_data[entry_id] = clean_items

            # --- Standard Handling ---
            else:
                # Find the Correct Option (handles the dash mismatches automatically)
                submission_data[entry_id] = find_correct_option(col_header, raw_value)

    # Submit
    try:
        response = requests.post(FORM_URL, data=submission_data)
        if response.status_code == 200:
            print(f"Row {index + 1}: Success")
            success_count += 1
        else:
            print(f"Row {index + 1}: FAILED (Status {response.status_code})")
            fail_count += 1
    except Exception as e:
        print(f"Row {index + 1}: Error {e}")
        fail_count += 1

    time.sleep(1)

print(f"Done. Success: {success_count} | Failed: {fail_count}")