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
import threading


def get_data(url):

    options = Options()
    options.add_argument("--window-position=-2400,-2400")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
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
        print("{MapBanTool}\tget_data :NoSuchElementException blocked")
    except TimeoutException:
        print("{MapBanTool}\tget_data : TimeoutException blocked")
    finally:
        real_bans = []
        for ban in bans:
            real_bans.append(ban.text)

    driver.quit()
    return real_bans

def get_rooms(url):

    options = Options()
    options.add_argument("--window-position=-2400,-2400")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
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
        print("{MapBanTool}\tget_rooms : NoSuchElementException blocked")
    except TimeoutException:
        print("{MapBanTool}\tget_rooms : TimeoutException blocked")
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

def update_config(setting,change):
    with open("src/config.txt",'r') as f:
        config = f.readlines()
    i = 0
    for s in config:
        i = s.find(setting)
        if(i != -1):
            break
    config[i] = setting+'='+change +'\n'
    with open("src/config.txt",'w') as f:
        for line in config:
            f.write(line)
    return

def print_periodically():
    while True:
        print('{MapBanTool}\t.')
        time.sleep(0.1)

def main():
    url = input('{MapBanTool}\tEnter URL of team to scrape data : \n')
    try:
        rooms = get_rooms(url)
    except InvalidArgumentException:
        print("{MapBanTool}\tGive a valid team URL")
        return
    
    newkey = rooms.pop()
    
    open('src/data.txt','w').close()
    i = 1
    all_bans = []
    for url in rooms:
        bans = get_data(url)
        for ban in bans:
            all_bans.append(ban)
        print("{MapBanTool}\tCollected data from ",url,'\t', i,'/',len(rooms))
        i+=1
    with open("src/data.txt","a") as f:
        for ban in all_bans:
            f.write(ban)
            f.write('\n')

    update_config("key",newkey)
    print("{MapBanTool}\tCleaning up...")



main()
quit()