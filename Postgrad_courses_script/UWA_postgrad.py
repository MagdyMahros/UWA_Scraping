"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 20-10-20
    * description:This script extracts the corresponding Postgraduate courses details and tabulate it.
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
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': 'IELTS',
               'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '6.5', 'Prerequisite_2_grade': '',
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

    # COURSE LANGUAGE
    for language in possible_languages:
        if language in course_data['Course']:
            course_data['Course_Lang'] = language
        else:
            course_data['Course_Lang'] = 'English'
    print('COURSE LANGUAGE: ', course_data['Course_Lang'])

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
                                                    .replace('0.5-1', '1').replace('4-8', '8').replace('Up', '2').
                                                    replace('12-18', '18'))
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
                            course_data[
                                'Remarks'] = 'The duration for this course stated in the website as "Not Applicable"'
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
                            course_data['Remarks'] = 'The duration for this course stated in the website as "Not Applicable"'
                    course_data['Duration'] = duration_num
                    course_data['Duration_Time'] = duration_time
                    print('DURATION / DURATION TIME: ', str(duration_num) + ' / ' + str(duration_time))

                # FULL_TIME / PART_TIME
                full_part_time_tag = dynamic_info_card.find_next('div', class_='card-details-label',
                                                                 text=re.compile('Attendance', re.IGNORECASE))
                if full_part_time_tag:
                    full_part_time_list = full_part_time_tag.find_next('div', class_='card-details-value').\
                        find('ul', class_='chevron-before-list').get_text().strip().replace('\n', ' / ')
                    # print('FULL-TIME / PART-TIME: ', full_part_time_list)
                    if 'Part-time' in full_part_time_list:
                        course_data['Part_Time'] = 'yes'
                    else:
                        course_data['Part_Time'] = 'no'
                    if 'Full-time' in full_part_time_list:
                        course_data['Full_Time'] = 'yes'
                    else:
                        course_data['Full_Time'] = 'no'
                    print('FULL-TIME: ', course_data['Full_Time'])
                    print('PART-TIME: ', course_data['Part_Time'])

                # DELIVERY (online, offline, face-to-face, blended, distance)
                delivery_tag = dynamic_info_card.find_next('div', class_='card-details-label',
                                                           text= re.compile('Delivery', re.IGNORECASE))
                if delivery_tag:
                    delivery_list = delivery_tag.find_next('div', class_ = 'card-details-value').\
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

                # CITY
                location_tag = dynamic_info_card.find_next('div', class_='card-details-label',
                                                           text=re.compile('Locations', re.IGNORECASE))
                if location_tag:
                    locations = location_tag.find_next('div', class_='card-details-value').\
                        find('ul', class_='chevron-before-list').find_all('li')
                    if locations:
                        for city in locations:
                            city = city.get_text().__str__().strip().split()[0].lower()
                            actual_cities.append(city)
                    else:
                        actual_cities.append('perth')
                    print('CITY: ', actual_cities)


            # AVAILABILITY
            course_code_Tag = dynamic_info_card.find_next('div', class_='card-details-label',
                                                          text=re.compile('Course Code', re.IGNORECASE))
            if course_code_Tag:
                course_code_list = course_code_Tag.find_next('div', class_='card-details-value').find('ul',
                                                                                                      class_='chevron-before-list').get_text().strip()
                if 'not available to international' in course_code_list:
                    course_data['Availability'] = 'D'
                else:
                    course_data['Availability'] = 'A'
            print('AVAILABILITY: ', course_data['Availability'])

            #CLOCK THE X BUTTON TO EXIT THE DYNAMIC DETAILS CARD
            try:
                browser.execute_script("arguments[0].click();", WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="modaal-close"]'))))
            except TimeoutException:
                print('Timeout Exception')
                pass
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
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance', 'Face_to_Face',
                          'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('UWA_postgradute_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)















