"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 20-10-20
    * description:This script extracts the corresponding Bachelor courses details and tabulate it.
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

course_data = {'Level_Code': '', 'University': 'Australian Catholic University', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': '',
               'Prerequisite_2': 'IELTS', 'Prerequisite_3': '', 'Prerequisite_1_grade': '', 'Prerequisite_2_grade': '6.5',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': 'A', 'Description': '',
               'Career_Outcomes': '', 'Online': 'no', 'Offline': 'yes', 'Distance': 'no', 'Face_to_Face': 'yes',
               'Blended': 'no', 'Remarks': ''}

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
        d_description = soup.find('div', class_='degree-details cards') \
            .find('div', class_='module-titles').find('p', class_='module-sub-title').text.strip().replace('\n', '')
        if '.' in d_description:  # Just to make sure the tag has text in it because there r some tags has no text
            course_data['Description'] = d_description
            print(d_description)
    # FOR MAJORS
    if soup.find('div', class_='course-details cards'):
        m_description = soup.find('div', class_='course-details cards') \
            .find('div', class_='module-titles').find('div', class_='module-sub-title').text.strip().replace('\n', '')
        course_data['Description'] = m_description
        print(m_description)
    # FOR SOME WEIRD DEGREE PAGES THAT HAS DIFFERENT STRUCTURE
    if soup.find('div', class_='degree-details cards'):
        d_description = soup.find('div', class_='degree-details cards') \
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
            atar_tag_3 = atar_tag_2.find('ul', class_='chevron-before-list')
            if atar_tag_3:
                atar = atar_tag_3.find('li')
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
        atar_tag_2_ = atar_tag_1_.find_previous('div', class_='course-header-module-stat-number') \
            .get_text().__str__().strip()
        # print(atar_tag_2_)
        course_data['Prerequisite_1_grade'] = atar_tag_2_
        course_data['Prerequisite_1'] = 'year 12'

    # DURATION & DURATION_TIME
    duration_tag = soup.find('div', class_='card-details-label', text=re.compile('full time', re.IGNORECASE))
    availability_list = []
    if duration_tag:
        duration_text = duration_tag.find_next('div', class_='card-details-value').find('ul').find('li') \
            .get_text().__str__().strip()
        duration_number = re.search(r'\d+', duration_text).group()
        print(duration_number)
        course_data['Duration'] = duration_number
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
        course_data['Duration'] = duration_number
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
        course_data['Duration'] = duration_number
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
        course_data['Duration'] = duration_number
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
        availability_text = availability_tag.find_next('div', class_='card-details-value') \
            .find('ul').get_text().__str__().strip()
        # print('availability ', availability_text.lower())
        availability_list.append(availability_text.lower())
        for element in availability_list:
            if 'full-time' in element.lower():
                course_data['Full_Time'] = 'yes'
            if 'part-time' in element.lower():
                course_data['Part_Time'] = 'yes'

    # DELIVERY
    delivery_tag = soup.find('div', class_='card-details-label', text=re.compile('Delivery', re.IGNORECASE))
    if delivery_tag:
        delivery_list = delivery_tag.find_next('div', class_='card-details-value'). \
            find('ul', class_='chevron-before-list').get_text().strip().replace('\n', ' / ')
        if 'On-campus' in delivery_list:
            course_data['Offline'] = 'yes'
            course_data['Face_to_Face'] = 'yes'
        else:
            course_data['Offline'] = 'no'
            course_data['Face_to_Face'] = 'no'
        if 'Off-campus' in delivery_list:
            course_data['Distance'] = 'yes'
        else:
            course_data['Distance'] = 'no'
        if 'Online' in delivery_list:
            course_data['Online'] = 'yes'
        else:
            course_data['Online'] = 'no'
        if 'On-campus' in delivery_list and 'Off-campus' in delivery_list and 'Online' in delivery_list:
            course_data['Blended'] = 'yes'
        else:
            course_data['Blended'] = 'no'
        print('ONLINE: ', course_data['Online'])
        print('OFFLINE: ', course_data['Offline'])
        print('FACE_TO_FACE: ', course_data['Face_to_Face'])
        print('DISTANCE: ', course_data['Distance'])
        print('BLENDED: ', course_data['Blended'])
    else:
        print('ONLINE: ', course_data['Online'])
        print('OFFLINE: ', course_data['Offline'])
        print('FACE_TO_FACE: ', course_data['Face_to_Face'])
        print('DISTANCE: ', course_data['Distance'])
        print('BLENDED: ', course_data['Blended'])

    # CITY
    locations_card = soup.find('div', class_='card-details-label', text=re.compile('Locations', re.IGNORECASE))
    if locations_card:
        locations = locations_card.find_next('div', class_='card-details-value') \
            .find('ul', class_='chevron-before-list').find_all('li')
        for city in locations:
            city = city.get_text().__str__().strip().split()[0].lower()
            actual_cities.append(city)

    # COURSE LANGUAGE
    for language in possible_languages:
        if language in course_data['Course']:
            course_data['Course_Lang'] = language
        else:
            course_data['Course_Lang'] = 'English'
    print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # CAREER OUTCOME
    # navigate to careers & further study tab
    try:
        browser.execute_script("arguments[0].click();", WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'CAREERS & FURTHER STUDY'))))
    except TimeoutException:
        print('Timeout Exception')
        pass
    # get the data
    out_come_card = soup.find('h3', class_='card-title', text=re.compile('Related careers', re.IGNORECASE))
    out_come_card2 = soup.find('h3', class_='card-title', text=re.compile('Career opportunities', re.IGNORECASE))
    outcome_list = []
    if out_come_card:
        data_container = out_come_card.find_next('div', class_='card-container'). \
            find('div', class_='card-content rich-text-content').find('ul')
        if data_container:
            print(data_container.get_text().__str__().strip().replace('\n', ' / '))
            course_data['Career_Outcomes'] = data_container.get_text().__str__().strip().replace('\n', ' / ')
    elif out_come_card2:
        data_container = out_come_card2.find_next('div', class_='card-container')
        if data_container:
            career_tag = data_container.find('div', class_='card-content rich-text-content')
            if career_tag:
                career_tag.find('ul', class_='chevron-before-list')
                print(career_tag.get_text().__str__().strip().replace('\n', ' / '))
                course_data['Career_Outcomes'] = career_tag.get_text().__str__().strip().replace('\n', ' / ')
            elif data_container.find('div').find_all('a', class_='card-rich-link'):
                career_list = data_container.find('div').find_all('a', class_='card-rich-link')
                if career_list:
                    for career in career_list:
                        # print(career.get_text().__str__().strip().replace('\n', ' / '))
                        outcome_list.append(career.get_text().__str__().strip().replace('\n', ' / '))
                outcome_list = ' / '.join(outcome_list)
                print(outcome_list.__str__().strip())
                course_data['Career_Outcomes'] = outcome_list.__str__().strip()

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

# TABULATE THE DATA
desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                      'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                      'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                      'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                      'Description','Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance', 'Face_to_Face',
                      'Blended', 'Remarks']

course_dict_keys = set().union(*(d.keys() for d in course_data_all))

with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, course_dict_keys)
    dict_writer.writeheader()
    dict_writer.writerows(course_data_all)

with open(csv_file, 'r', encoding='utf-8') as infile, open('UWA_bachelors_ordered.csv', 'w', encoding='utf-8',
                                                           newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
    # reorder the header first
    writer.writeheader()
    for row in csv.DictReader(infile):
        # writes the reordered rows to the new file
        writer.writerow(row)
