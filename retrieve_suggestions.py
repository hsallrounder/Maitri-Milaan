from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep

def get_sug(input_city):
    url = "https://www.prokerala.com/astrology/kundali-matching-hindi.php"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    glocation = driver.find_element(By.ID,"fin_glocation")
    glocation.click()
    glocation.clear()
    glocation.send_keys(input_city)

    sleep(5)

    html_content = driver.page_source

    driver.quit()

    soup = BeautifulSoup(html_content, "html.parser")

    suggestions = soup.find_all("div", class_="autocomplete-suggestion")

    result=[]

    for suggestion in suggestions:
        location = suggestion["data-location"]
        city, state_country = location.split(", ", 1)
        state_country_parts = state_country.split(", ")
        if len(state_country_parts) == 1:
            state = ""
            country = state_country_parts[0]
        else:
            state = state_country_parts[0]
            country = state_country_parts[1]

        result.append({"city": city, "state": state, "country": country})
        
    return result
