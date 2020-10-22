"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 20-10-20
    * description:This program extracts the corresponding Bachelor courses details and tabulate it.
"""
import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import requests
import os
import copy
from CustomMethods import DurationConverter
from CustomMethods import TemplateData


option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)


# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/UWA_Bachelor_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/UWA_bachelors.csv'

course_data = {'Level_Code': '', 'University': 'University Of Western Australia', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': '',
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': '',
               'Prerequisite_1_grade': '', 'Website': '', 'Course_Lang': 'English', 'Availability': '', 'Study_Mode': '',
               'Description': '', 'Mode_of_Study': '', 'Study_Type': '', 'Online': '', 'Offline': ''}

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
    # FOR DEGREE
    if soup.find('h1', class_='degree-header-module-title'):
        course_title = soup.find('h1', class_='degree-header-module-title').text
        # print(course_title)
        course_data['Course'] = course_title.strip()
    # FOR MAJORS
    if soup.find('h1', class_='course-header-module-title'):
        course_title = soup.find('h1', class_='course-header-module-title').text
        # print(course_title)
        course_data['Course'] = course_title.strip()

    # DECIDE THE LEVEL CODE
    for i in level_key:
        for j in level_key[i]:
            if j in course_data['Course']:
                course_data['Level_Code'] = i
    # print(course_data['Level_Code'])

    # DECIDE THE FACULTY
    for i in faculty_key:
        for j in faculty_key[i]:
            if j.lower() in course_data['Course'].lower():
                course_data['Faculty'] = i
    # print(course_data['Faculty'])

    # COURSE DESCRIPTION
    # FOR DEGREE
    if soup.find('div', class_='degree-details cards'):
        d_description = soup.find('div', class_='degree-details cards')\
            .find('div', class_='module-titles').find('p', class_='module-sub-title').text.strip().replace('\n', '')
        if '.' in d_description:  # Just to make sure the tag has text in it because there r some tags has no text
            course_data['Description'] = d_description
            print(d_description)
    # FOR MAJORS
    if soup.find('div', class_='course-details cards'):
        m_description = soup.find('div', class_='course-details cards')\
            .find('div', class_='module-titles').find('div', class_='module-sub-title').text.strip().replace('\n', '')
        course_data['Description'] = m_description
        print(m_description)
    # FOR SOME WEIRD DEGREE PAGES THAT HAS DIFFERENT STRUCTURE
    if soup.find('div', class_='degree-details cards'):
        d_description = soup.find('div', class_='degree-details cards')\
            .find('div', class_='module-titles')
        if d_description:
            d_description_p = d_description.find_all('p')
            if len(d_description_p) == 3:
                d_description = d_description_p[1].text
                course_data['Description'] = d_description
                print(d_description)

    # Prerequisite 1 & ATAR
    # FOR DEGREE
    atar_tag_1 = soup.find('div', class_='card-details-label', text=re.compile('Minimum Atar', re.IGNORECASE))
    if atar_tag_1:
        atar_tag_2 = atar_tag_1.find_next('div', class_='card-details-value')
        if atar_tag_2:
            atar = atar_tag_2.find('ul', class_='chevron-before-list').find('li')
            atar_val = re.search(r'\d+', atar.get_text().__str__().strip()).group()
            if int(atar_val) in range(40, 99):
                atar_tag_3 = atar_val
                # print(atar_val)
                course_data['Prerequisite_1_grade'] = atar_val
                course_data['Prerequisite_1'] = 'year 12'
    # FOR MAJOR
    atar_tag_1_ = soup.find('div', class_='course-header-module-stat-subject',
                            text=re.compile('ATAR', re.IGNORECASE))
    if atar_tag_1_:
        atar_tag_2_ = atar_tag_1_.find_previous('div', class_='course-header-module-stat-number')\
            .get_text().__str__().strip()
        # print(atar_tag_2_)
        course_data['Prerequisite_1_grade'] = atar_tag_2_
        course_data['Prerequisite_1'] = 'year 12'

    # DURATION & DURATION_TIME
    duration_tag = soup.find('div', class_='card-details-label', text=re.compile('full time', re.IGNORECASE))
    availability_list = []
    if duration_tag:
        duration_text = duration_tag.find_next('div', class_='card-details-value').find('ul').find('li')\
            .get_text().__str__().strip()
        duration_number = re.search(r'\d+', duration_text).group()
        print(duration_number)
        course_data['Description'] = duration_number
        course_data['Full_Time'] = 'yes'
        if int(duration_number) > 1:
            course_data['Duration_Time'] = 'years'
        elif int(duration_number) == 1:
            course_data['Duration_Time'] = 'year'
        availability_list.append('full time')
    elif soup.find('div', class_='card-details-label', text=re.compile('full-time', re.IGNORECASE)):
        duration_tag = soup.find('div', class_='card-details-label', text=re.compile('full-time', re.IGNORECASE))
        duration_text = duration_tag.find_next('div', class_='card-details-value').find('ul').find('li') \
            .get_text().__str__().strip()
        duration_number = re.search(r'\d+', duration_text).group()
        print(duration_number)
        course_data['Description'] = duration_number
        course_data['Full_Time'] = 'yes'
        if int(duration_number) > 1:
            course_data['Duration_Time'] = 'years'
        elif int(duration_number) == 1:
            course_data['Duration_Time'] = 'year'
        availability_list.append('full time')
    elif soup.find('div', class_='card-details-label', text=re.compile('part time', re.IGNORECASE)):
        duration_tag = soup.find('div', class_='card-details-label', text=re.compile('part time', re.IGNORECASE))
        duration_text = duration_tag.find_next('div', class_='card-details-value').find('ul').find('li') \
            .get_text().__str__().strip()
        duration_number = re.search(r'\d+', duration_text).group()
        print(duration_number)
        course_data['Description'] = duration_number
        course_data['Part_Time'] = 'yes'
        if int(duration_number) > 1:
            course_data['Duration_Time'] = 'years'
        elif int(duration_number) == 1:
            course_data['Duration_Time'] = 'year'
        availability_list.append('part time')
    elif soup.find('div', class_='card-details-label', text=re.compile('part-time', re.IGNORECASE)):
        duration_tag = soup.find('div', class_='card-details-label', text=re.compile('part-time', re.IGNORECASE))
        duration_text = duration_tag.find_next('div', class_='card-details-value').find('ul').find('li') \
            .get_text().__str__().strip()
        duration_number = re.search(r'\d+', duration_text).group()
        print(duration_number)
        course_data['Description'] = duration_number
        course_data['Part_Time'] = 'yes'
        if int(duration_number) > 1:
            course_data['Duration_Time'] = 'years'
        elif int(duration_number) == 1:
            course_data['Duration_Time'] = 'year'
        availability_list.append('part time')
    if 'part time' not in availability_list:
        course_data['Part_Time'] = 'no'


    # FULL_TIME/PART_TIME
    availability_tag = soup.find('div', class_='card-details-label', text=re.compile('ATTENDANCE', re.IGNORECASE))
    if availability_tag:
        availability_text = availability_tag.find_next('div', class_='card-details-value')\
            .find('ul').get_text().__str__().strip()
        # print('availability ', availability_text.lower())
        availability_list.append(availability_text.lower())
        for element in availability_list:
            if 'full-time' in element.lower():
                course_data['Full_Time'] = 'yes'
            if 'part-time' in element.lower():
                course_data['Part_Time'] = 'yes'

    # CITY
    locations_card = soup.find('div', class_='card-details-label', text=re.compile('Locations', re.IGNORECASE))
    if locations_card:
        locations = locations_card.find_next('div', class_='card-details-value')\
            .find('ul', class_='chevron-before-list').find_all('li')
        for city in locations:
            city = city.get_text().__str__().strip().split()[0].lower()
            actual_cities.append(city)

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities






