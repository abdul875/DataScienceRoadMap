import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 1. CONFIGURATION
# ==========================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeApSvFONQOQAl2wCEL_lTK4zuDEKq_mHtcoTL6qUHu1FeA4w/viewform"

# Map CSV Column Name --> Partial Text of Question Title on the Google Form
# This ensures we find the exact question box, even if "Yes/No" appears multiple times.
QUESTION_MAPPING = {
    "What is your age?": "What is your age",
    "What is your occupation?": "What is your occupation",
    "What is your marital status?": "What is your marital status",
    "Do you have any of these?": "Do you have any of these",
    "Are your menstrual cycles regular and What is the average length of your menstrual cycle (in days)?": "Are your menstrual cycles regular",
    "Do you experience pain or cramps during menstruation?": "Do you experience pain or cramps",
    "Do you ever miss your periods for more than two months (without pregnancy)?": "Do you ever miss your periods",
    "Do you experience excessive or very light bleeding?": "Do you experience excessive",
    "How often do you usually skip meals in a day?": "How often do you usually skip meals",
    "Do you take meals exactly on time?": "Do you take meals exactly on time",
    "How often do you consume fast food or street food in a week?": "How often do you consume fast food",
    "Do you consume sugary or carbonated drinks regularly?": "Do you consume sugary",
    "How often do you eat green leafy vegetables and fruits per week?": "How often do you eat green leafy",
    "Do you take any dietary supplements (e.g., iron, multivitamins)? If yes which one?": "Do you take any dietary supplements",
    "Do you believe that food habits, stress or poor diet can cause irregular periods and why?": "Do you believe that food habits",
    "Are you aware of the importance of iron and calcium-rich foods during menstruation?": "Are you aware of the importance",
    "Have you ever been informed (by doctor, teacher, or media) about the link between diet and menstrual health?": "Have you ever been informed",
    "Would you be willing to change your diet if you knew it would improve menstrual regularity and reduce pain?": "Would you be willing to change"
}

# Questions that allow multiple answers (Checkboxes)
CHECKBOX_QUESTIONS = ["Do you have any of these"]


# ==========================================
# 2. HELPER: FUZZY CLEANER
# ==========================================
def clean_str(s):
    """Removes all non-alphanumeric chars for comparison. '1-2' == '1–2'"""
    return re.sub(r'[^a-zA-Z0-9]', '', str(s).lower())


# ==========================================
# 3. SELENIUM SETUP
# ==========================================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

try:
    df = pd.read_csv('F:\Data Science Journey\DataScienceRoadMap\practice_code\Thisis_Data_JU_heet1.csv')
    df = df.fillna("")
    print(f"Loaded {len(df)} rows.")
except Exception as e:
    print("Error reading data.csv:", e)
    exit()

# ==========================================
# 4. MAIN LOOP
# ==========================================
for index, row in df.iterrows():
    print(f"\nProcessing Row {index + 1}...")
    driver.get(FORM_URL)

    # Wait for form to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='listitem']")))

    row_failed = False

    for col_header, question_text in QUESTION_MAPPING.items():
        if col_header not in df.columns: continue

        user_answer = str(row[col_header]).strip()
        if not user_answer: continue

        try:
            # 1. FIND THE QUESTION CONTAINER
            # We look for a container that has the specific question title text
            q_xpath = f"//div[@role='listitem']//span[contains(text(), '{question_text}')]/../../../../.."
            question_container = driver.find_element(By.XPATH, q_xpath)

            # 2. CHECK IF IT IS A TEXT INPUT
            inputs = question_container.find_elements(By.TAG_NAME, "input") + question_container.find_elements(
                By.TAG_NAME, "textarea")
            # Filter out hidden inputs
            visible_inputs = [i for i in inputs if i.get_attribute("type") != "hidden"]

            if visible_inputs:
                # It's a text question, type the answer
                visible_inputs[0].clear()
                visible_inputs[0].send_keys(user_answer)
                # print(f"  - Typed '{user_answer}' for '{question_text}'")

            # 3. CHECK IF IT IS RADIO/CHECKBOX
            else:
                # Get all clickable options in this specific question container
                options = question_container.find_elements(By.XPATH, ".//div[@role='radio'] | .//div[@role='checkbox']")

                # Handle multiple answers (for Checkboxes)
                targets = user_answer.split(',') if any(c in question_text for c in CHECKBOX_QUESTIONS) else [
                    user_answer]

                for target in targets:
                    target_clean = clean_str(target)
                    clicked = False

                    for opt in options:
                        # Get the value Google stored in the HTML (e.g. "1–2 times")
                        data_val = opt.get_attribute("data-value") or opt.get_attribute("data-answer-value")
                        if not data_val: continue

                        # Compare cleaned strings (ignores dash types)
                        if clean_str(data_val) == target_clean:
                            driver.execute_script("arguments[0].click();", opt)
                            clicked = True
                            break

                    if not clicked:
                        print(f"  [ERROR] Option match failed! Question: '{question_text}' | CSV Value: '{target}'")
                        row_failed = True

        except Exception as e:
            print(f"  [ERROR] Could not find question: '{question_text}'. Error: {e}")
            row_failed = True

    # --- SUBMIT ---
    if not row_failed:
        try:
            # Click by ID (Language independent)
            submit_btn = driver.find_element(By.XPATH, "//div[@role='button' and @jsname='M2UYVd']")
            driver.execute_script("arguments[0].click();", submit_btn)

            # Check success
            time.sleep(2)
            if "formResponse" in driver.current_url:
                print(f"Row {index + 1}: SUCCESS")
            else:
                print(f"Row {index + 1}: FAILED (Form Validation Blocked Submission)")
        except:
            print(f"Row {index + 1}: FAILED (Button not found)")
    else:
        print(f"Row {index + 1}: SKIPPED (Data mismatch)")

    time.sleep(1)

print("Done.")
driver.quit()