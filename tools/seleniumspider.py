from selenium import webdriver
browser = webdriver.Chrome(executable_path="E:/pythonProject/seleniumdriver/chromedriver.exe")
browser.get("https://www.zhihu.com/signin?next=%2F")

browser.find_element_by_css_selector()