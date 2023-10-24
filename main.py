from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time

URL = "https://orteil.dashnet.org/cookieclicker/"
WAIT = 10
TIME_LIMIT = time.time() + 60 * 5

def initialize_driver():
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

def click_popup(driver, by, value):
    try:
        element = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((by, value)))
        element.click()
    except Exception:
        pass

def close_achievements(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, ".framed.close.sidenote").click()
    except NoSuchElementException:
        pass

def purchase_upgrades(driver):
    money = driver.find_element(By.ID, "cookies").text
    if "," in money:
        money = money.replace(",", "")
    cookie_count = int(money.split(" ")[0])

    while True: 
        try:
            all_prices = WebDriverWait(driver, WAIT).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "price")))
            item_prices = [int(price.text.replace(",", "")) for price in all_prices if price.text != "" and "million" not in price.text]
        except (StaleElementReferenceException, NoSuchElementException):
            continue

        item_ids = [item.get_attribute("id") for item in driver.find_elements(By.CSS_SELECTOR, "#products > [id^='product']")]

        cookie_upgrades = dict(zip(item_prices, item_ids))
        affordable_upgrades = {cost: id for cost, id in cookie_upgrades.items() if cookie_count > cost}

        if affordable_upgrades:
            expensive_upgrade = max(affordable_upgrades)
            to_purchase_id = affordable_upgrades[expensive_upgrade]

            try:
                upgrade_element = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, to_purchase_id)))
                upgrade_element.click()
            except (StaleElementReferenceException, NoSuchElementException):
                continue

        break

def main():
    driver = initialize_driver()
    driver.get(URL)

    click_popup(driver, By.CLASS_NAME, "fc-primary-button")
    click_popup(driver, By.ID, "langSelect-EN")
    time.sleep(2)
    click_popup(driver, By.LINK_TEXT, "Got it!")
    click_popup(driver, By.CSS_SELECTOR, "img[aria-label='Close']")


    cookie = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, "bigCookie"))) 
    timeout = time.time() + 5

    while True:
        cookie.click()
        close_achievements(driver)

        if time.time() > timeout:
            purchase_upgrades(driver)
            timeout = time.time() + 5
       
        if time.time() > TIME_LIMIT:           
            try:
                cookie_per_sec = WebDriverWait(driver, WAIT).until(
                    EC.presence_of_element_located((By.ID, "cookiesPerSecond"))
                ).text
                print(cookie_per_sec)
            except StaleElementReferenceException:
                continue
            break
    
    driver.quit()

main()