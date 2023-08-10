from requests import request
from bs4 import BeautifulSoup
import requests
import LaTeX2img
from selenium.webdriver.common.by import By
import os

def tt(index, a, b, browser):
    
    # #latex2png
    # formula = browser.find_element("id", "form_latex")
    # formula.clear()
    # formula.send_keys(a)
    
    # button = browser.find_element("id", "convert_button")
    # a = button.click()

    # import time
    # time.sleep(8) # Sleep for 1 seconds
    
    # soup = BeautifulSoup(browser.page_source, 'html.parser')
    # div_element = soup.find('div', id='dialog')
    # style_value = div_element.get('style')
    
    # if(style_value == 'display: none;'):
    #     img = browser.find_element("id", "img_output")
    #     image_src = img.get_attribute('src')
        
    #     response = requests.get(image_src)
        
    #     with open(f"images/{index}/{b}.png", "wb") as file:
    #         file.write(response.content)
    #         print("图像下载成功！")
    # else:
    #     button_2 = browser.find_element("id", "dialog_okay")
    #     button_2.click()
    
    #mathURL
    formula = browser.find_element("id", "latex")
    formula.clear()
    formula.send_keys(a)
    
    
    import time
    time.sleep(5) # Sleep for 1 seconds
    
    
    img = browser.find_element("id", "image")
    image_src = img.get_attribute('src')
    
    response = requests.get(image_src)
    
    with open(f"images/{index}/{b}.png", "wb") as file:
        file.write(response.content)
        print("图像下载成功！")

def toimg(index, a, b, browser):
    global miss, count
    
    os.makedirs(f'images/{index}', exist_ok=True)
    try:
        tt(index, a, "ground", browser)
        tt(index, b, "predict", browser)
        a = LaTeX2img.lateximage(index)
        return a
    except:
        return -1

def success(count,miss):
    print("success : "+str(count))
    print("miss : "+str(miss))
    return [count, miss]
