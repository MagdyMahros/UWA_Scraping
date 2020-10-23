"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 20-10-20
    * description:This script extracts the corresponding Post graduate courses details and tabulate it.
"""
import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)


# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/UWA_Postgrad_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/UWA_postgradute.csv'

course_data = {'Level_Code': '', 'University': 'Australian Catholic University', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': '',
               'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '', 'Prerequisite_2_grade': '',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': '', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': '', 'Face_to_Face': '',
               'Blended': '', 'Remarks': ''}

possible_cities = {'albany': 'Albany', 'perth': 'Perth'}
possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # SAVE COURSE TITLE
    course_title = soup.find('h1', class_='course-header-module-title').text
    if course_title:
        print('COURSE TITLE: ', course_title)
        course_data['Course'] = course_title.strip()

    # DECIDE THE LEVEL CODE
    for i in level_key:
        for j in level_key[i]:
            if j in course_data['Course']:
                course_data['Level_Code'] = i
    print('COURSE LEVEL CODE: ', course_data['Level_Code'])

    # DECIDE THE FACULTY
    for i in faculty_key:
        for j in faculty_key[i]:
            if j.lower() in course_data['Course'].lower():
                course_data['Faculty'] = i
    print('COURSE FACULTY: ', course_data['Faculty'])

    # COURSE DESCRIPTION
    d_title = soup.find('h2', class_='module-title', text=re.compile('Course details', re.IGNORECASE))
    if d_title:
        description = d_title.find_next('div', class_='module-sub-title')
        print('COURSE DESCRIPTION: ', description.get_text())
        course_data['Description'] = description.get_text()

    # TODO: FIND PREREQUISITES

    # DURATION & DURATION_TIME
    details_card_title = soup.find('h3', class_='card-title', text=re.compile('Quick details', re.IGNORECASE))
    if details_card_title:
        button = details_card_title.find_next('a', class_='cta-row-link modal-hook')
        if button:
            try:
                browser.execute_script("arguments[0].click();", WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'View full details'))))
            except TimeoutException:
                print('Timeout Exception')
                pass
            # grab the information
            dynamic_info_card = details_card_title.find_next('div', class_='card-details card-details-dynamic')
            if dynamic_info_card:
                duration_tag = dynamic_info_card.find_next('div', class_='card-details-label',
                                                           text=re.compile('duration', re.IGNORECASE))
                if duration_tag:
                    duration = duration_tag.find_next('div', class_='card-details-value')
                    duration_num = dura.convert_num(duration.get_text().strip().split()[0].replace('1.5-2', '1.5').
                                                    replace('2.5-3', '2.5').replace('1-2', '2').replace('2-3', '3')
                                                    .replace('0.5-1', '1').replace('4-8', '8').replace('Up', '2').replace('12-18', '18'))
                    duration_time = None
                    if len(duration.get_text().strip().split()) == 2:
                        if str(duration_num) == '0.5':
                            duration_num = '6'
                        if 'Not' not in duration_num:
                            if str(duration_num) == '1' and 'Semester' not in duration.get_text().strip().split()[1]:
                                duration_time = 'year'
                            elif str(duration.get_text().strip().split()[1]) == 'Semester':
                                duration_num = '6'
                                duration_time = 'months'
                            elif float(duration_num) > 5:
                                duration_time = 'months'
                            else:
                                duration_time = 'years'
                        else:
                            duration_num = 'N/A'
                            duration_time = 'N/A'
                    else:
                        if 'Not' not in duration_num:
                            if str(duration_num) == '1':
                                duration_time = 'year'
                            elif float(duration_num) > 5:
                                duration_time = 'months'
                            else:
                                duration_time = 'years'
                        else:
                            duration_num = 'N/A'
                            duration_time = 'N/A'
                    course_data['Duration'] = duration_num
                    course_data['Duration_Time'] = duration_time
                    print('DURATION / DURATION TIME: ', str(duration_num) + ' / ' + str(duration_time))























