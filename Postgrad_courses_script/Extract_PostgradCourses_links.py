"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 20-10-20
    * description:This script extracts all the courses links and save it in txt file.
"""
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os


option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# MAIN ROUTINE
courses_page_url = 'https://www.uwa.edu.au/study/courses-and-careers/find-a-course?level=Postgraduate&term='
list_of_links = []
browser.get(courses_page_url)
delay_ = 5  # seconds

# KEEP CLICKING UNTIL THERE IS NO BUTTON
condition = True
while condition:
    try:
        browser.execute_script("arguments[0].click();", WebDriverWait(browser, delay_).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "div > div:nth-child(2) > div > div > div:nth-child(3) "
                                        "> div.results-action > button.results-action-load-more"))))
    except TimeoutException:
        condition = False

# EXTRACT ALL THE LINKS TO LIST
result_elements = browser.find_elements_by_class_name('result-item')
for element in result_elements:
    link = element.get_property('href')
    list_of_links.append(link)

# SAVE TO FILE
course_links_file_path = os.getcwd().replace('\\', '/') + '/UWA_Postgrad_links.txt'
course_links_file = open(course_links_file_path, 'w')
for link in list_of_links:
    if link is not None and link != "" and link != "\n":
        if link == list_of_links[-1]:
            course_links_file.write(link.strip())
        else:
            course_links_file.write(link.strip() + '\n')
course_links_file.close()



