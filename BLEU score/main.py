import toimg
import os
from requests import request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗

browser = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=options)

# browser.get("https://latex2image.joeraut.com/")
# browser.get("https://products.aspose.app/tex/equation-editor/png")
# browser.get("https://latex2png.com/")
browser.get("http://mathurl.com/")

# all = os.listdir("E:/new_proj/output")
score = -1
total_score = 0
i = 0
wrong = []
flag = True
# for i,work in enumerate(all):
    
#     if work == "100913":
#         flag = False
#         continue
#     if flag :
#         continue
#     print("now:",work)
#     print(os.path.exists("E:/new_proj/output/"+work+"/"+work+"result.txt"))
#     with open ("E:/new_proj/output/"+work+"/"+work+".txt", "r") as w:
#         with open ("E:/new_proj/output/"+work+"/"+work+"result.txt", "r") as w2:
    
    
# formula = browser.find_element("id", "form_latex")
# formula.clear()
# button = browser.find_element("id", "convert_button")
# a = button.click()


import time
time.sleep(5)



with open('wrong.txt', 'r') as file:
    content = file.read()
lines = content.split('\n')


for index, math in enumerate(lines):
    # if index > 53456*3 and index < 60001*3:
    if index % 5 == 0:
        i += 1
        num = lines[index]
        if int(num) >= 53367:
            l = lines[index + 1]
            l2 = lines[index + 2]
        
            t = toimg.toimg(num, l, l2, browser)
    
            if(t == -1):
                wrong.append(num)
                wrong.append(l)
                wrong.append(l2)
                wrong.append("\n")
                with open ("wrong2.txt", "a") as wr:
                    for j in wrong:
                        wr.write(str(j)+"\n")
                wrong = []
            
            else:
                score = t
                total_score += t
                with open ("./score/"+ str(index//3) +"_score.txt", "w") as sc:
                    sc.write("score : "+str(score)+"\n")
                    print("score: ",score)
        
        
# print("total score: ",total_score / i)
browser.quit()
    
