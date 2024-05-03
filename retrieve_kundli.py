from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup
import json

def ist24_to_ist12(tobinist):
    # Example 24-hour time string
    time_str = tobinist

    # Parse the time string into a datetime object
    time_obj = datetime.strptime(time_str, "%H:%M")

    # Extract hour and minute components
    hour = time_obj.strftime("%I")  # Format hour as 01/02 in 12-hour format
    minute = time_obj.strftime("%M")  # Format minute as 01/02

    # Determine AM/PM
    am_pm = time_obj.strftime("%p")

    return [hour, minute, am_pm]

def extract_date(dob):
    # Example date string in yyyy-mm-dd format
    date_str = dob

    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Extract year, month, and day components
    year = str(date_obj.year)
    month = str(date_obj.strftime("%b"))
    day = str(date_obj.day)

    return [year, month, day]

def find_data(email, user_data_ref):

    ref = user_data_ref

    data = ref.child(email.replace('.', ',')).get()

    pob_parts = data["pob"].split(", ")
    pob = pob_parts[0]+", "+pob_parts[1].split(" ")[0][:-2]

    tob = ist24_to_ist12(data["tobinist"])
    print(tob)

    dob = extract_date(data["dob"])

    detail={
        "name":data["name"],
        "pob":pob,
        "year":dob[0],
        "month":dob[1],
        "day":dob[2],
        "hr":tob[0],
        "mn":tob[1],
        "apm":tob[2],
    }
    return detail

def form_fill(gdetail,bdetail):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches',["enable-automation"])
    options.add_experimental_option("useAutomationExtension",False)

    driver = webdriver.Chrome(options=options)

    driver.get("https://www.prokerala.com/astrology/kundali-matching-hindi.php") 

    gname = driver.find_element(By.ID,"fin_gname")
    gname.click()
    gname.clear()
    gname.send_keys(gdetail["name"])
    
    glocation = driver.find_element(By.ID,"fin_glocation")
    glocation.click()
    glocation.clear()
    glocation.send_keys(gdetail["pob"])
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".autocomplete-suggestions[style*='display: block']"))
    )
    glocation.send_keys(Keys.ARROW_DOWN)
    glocation.send_keys(Keys.RETURN)

    gyear = Select(driver.find_element(By.ID,"fin_gyear"))
    gyear.select_by_visible_text(gdetail["year"])
    
    gmonth = Select(driver.find_element(By.ID,"fin_gmonth"))
    gmonth.select_by_visible_text(gdetail["month"])

    gday = Select(driver.find_element(By.ID,"fin_gday"))
    gday.select_by_visible_text(gdetail["day"])

    ghour = Select(driver.find_element(By.ID,"fin_ghour"))
    ghour.select_by_visible_text(gdetail["hr"])

    gmin = Select(driver.find_element(By.ID,"fin_gmin"))
    gmin.select_by_visible_text(gdetail["mn"])

    gapm = Select(driver.find_element(By.ID,"fin_gapm"))
    gapm.select_by_visible_text(gdetail["apm"])

    bname = driver.find_element(By.ID,"fin_bname")
    bname.click()
    bname.clear()
    bname.send_keys(bdetail["name"])
    
    blocation = driver.find_element(By.ID,"fin_blocation")
    blocation.click()
    blocation.clear()
    blocation.send_keys(bdetail["pob"])
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".autocomplete-suggestions[style*='display: block']"))
    )
    blocation.send_keys(Keys.ARROW_DOWN)
    blocation.send_keys(Keys.RETURN)
    

    byear = Select(driver.find_element(By.ID,"fin_byear"))
    byear.select_by_visible_text(bdetail["year"])

    bmonth = Select(driver.find_element(By.ID,"fin_bmonth"))
    bmonth.select_by_visible_text(bdetail["month"])

    bday = Select(driver.find_element(By.ID,"fin_bday"))
    bday.select_by_visible_text(bdetail["day"])

    bhour = Select(driver.find_element(By.ID,"fin_bhour"))
    bhour.select_by_visible_text(bdetail["hr"])

    bmin = Select(driver.find_element(By.ID,"fin_bmin"))
    bmin.select_by_visible_text(bdetail["mn"])

    bapm = Select(driver.find_element(By.ID,"fin_bapm"))
    bapm.select_by_visible_text(bdetail["apm"])

    driver.find_element(By.ID,"astro-submit-button").click()

    sleep(5)

    html_content = driver.page_source
    
    driver.quit()
    
    with open("milaan_result.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    return html_content

def extract_info(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the first element with class="alert" and get its color
    first_alert = soup.find(class_="alert")
    result_color = color = None
    if 'alert-danger' in first_alert['class']:
        result_color = 'score red'
    elif 'alert-success' in first_alert['class']:
        result_color = 'score green'
    
    # Extract the score from the second table if it exists
    score = soup.find(class_="t-xxlarge").text.split(" ")[-3].strip()
    
    # Prepare the extracted information as a dictionary
    extracted_info = {
        "result_color": result_color,
        "score": score
    }

    return extracted_info

def find_kundli_milan(gdetail, bdetail):
    html_content = form_fill(gdetail, bdetail)
    
    extracted_info = extract_info(html_content)
    
    return extracted_info