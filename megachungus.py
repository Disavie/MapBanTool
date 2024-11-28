import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import InvalidArgumentException

def get_data(url):

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    delay = 2
    mapbans_class_name = 'HistoryItem__Li-sc-dcb0c0ec-0.dfJFLi'
    veto_history_link_xpath ="//span[@data-testid='mapsVetoHistory']"
    driver.get(url)
    bans = []
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, veto_history_link_xpath)))
        vetobutton = driver.find_element(By.XPATH,veto_history_link_xpath)
        vetobutton.click()
        bans = driver.find_elements(By.CLASS_NAME,mapbans_class_name)
    except NoSuchElementException:
        print("get_data :NoSuchElementException blocked")
    except TimeoutException:
        print("get_data : TimeoutException blocked")
    finally:
        real_bans = []
        for ban in bans:
            real_bans.append(ban.text)

    driver.quit()
    return real_bans

def get_rooms(url):

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    teamname_class_name = 'HeadingBase-sc-63d0bc6b-0.bcBbHa.styles__Nickname-sc-cdc2b4d0-5.gclupW'
    rooms_class_name = 'Faction__Holder-sc-ff737785-0 kfDrX'
    urls = []
    delay = 10
    driver.get(url)
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/en/ow2/room/')]")))
        urls = driver.find_elements(By.XPATH, "//a[contains(@href, '/en/ow2/room/')]")
    except NoSuchElementException:
        print("get_rooms : NoSuchElementException blocked")
    except TimeoutException:
        print("get_rooms : TimeoutException blocked")
    finally:
        real_urls = []
        for roomurl in urls:
            real_urls.append(roomurl.get_attribute("href"))
    
    elem = driver.find_element(By.CLASS_NAME,teamname_class_name)
    key = elem.text
    index = key.find('(')
    if index != -1:
        result = key[:index]
    key = result
    real_urls.append(key)
    driver.quit()
    return real_urls

def get_to_team_page(url):

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    class_name = 'styles__TeamMetaContainer-sc-a3d63a5e-0.gVFAMq'
    delay = 5
    urls_to_team_pages= []
    driver.get(url)
    myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    temps = driver.find_elements(By.CLASS_NAME, class_name)

    partial_link = '//a[contains(@href'
    teams_class = 'ButtonBase__Wrapper-sc-9fae6077-0.bwdpsX.Button__Base-sc-1203e5b2-0.jOUWgh'
    close_menu_class = 'styles__Backdrop-sc-f26c4043-0.kEZUJo'
    i = 0
    while(i<len(temps) and i < 16):
  
        temps[i].click()
        myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/en/teams/')]")))
        elem = driver.find_element(By.XPATH, "//a[contains(@href, '/en/teams/')]")
        urls_to_team_pages.append(elem.get_attribute("href"))
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        i+=1

    driver.quit()
    return urls_to_team_pages

def update_config(setting,change):
    with open("config.txt",'r') as f:
        config = f.readlines()
    i = 0
    for s in config:
        i = s.find(setting)
        if(i != -1):
            break
    config[i] = setting+'='+change +'\n'
    with open("config.txt",'w') as f:
        for line in config:
            f.write(line)
    return

def main():
    url = input('Enter URL of team to scrape data : \n')
    try:
        rooms = get_rooms(url)
    except InvalidArgumentException:
        print("Give a valid team URL")
        return
    
    newkey = rooms.pop()
    
    open('data.txt','w').close()
    i = 1
    for url in rooms:
        bans = get_data(url)
        print("Completed ", i,'/',len(rooms))
        i+=1
        with open("data.txt","a") as f:
            for ban in bans:
                f.write(ban)
                f.write('\n')

    update_config("key",newkey)
    return



main()