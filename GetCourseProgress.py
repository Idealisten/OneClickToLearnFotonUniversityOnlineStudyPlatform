from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

chrome = webdriver.Chrome()
chrome.implicitly_wait(10)
chrome.get("http://study.foton.com.cn")
chrome.maximize_window()


def login():
    account = "caoyue4"
    password = "aufwiedersehen2022$"

    ele = chrome.find_element_by_id("loginName")
    ele.click()
    ele.send_keys(account)

    ele = chrome.find_element_by_id("password")
    ele.click()
    ele.send_keys(password)

    time.sleep(1)
    ele = chrome.find_element_by_css_selector("#fm1 > input.btn.btn-block.btn-primary.btn-lg")
    ele.click()


def find_courses_progress():
    with open('course_progress.txt', 'w', encoding='utf-8') as f:
        f.write('课程名称,')
        f.write('课程ID,')
        f.write('课程学分,')
        f.write('结业条件,')
        f.write('学习进度\n')
        chrome.switch_to.frame(chrome.find_element_by_xpath('/html/body/div[2]/div[4]/div[2]/iframe'))
        time.sleep(3)
        # above = chrome.find_element_by_partial_link_text("学习中心")
        study_center = WebDriverWait(chrome, 15, 0.5).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, '学习中心')))
        time.sleep(1)
        ActionChains(chrome).move_to_element(study_center).perform()
        time.sleep(2)
        # above = chrome.find_element_by_link_text("课程中心")
        course_center = WebDriverWait(chrome, 15, 0.5).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, '课程中心')))
        course_center.click()
        time.sleep(5)
        chrome.switch_to.default_content()
        time.sleep(3)
        chrome.switch_to.frame(chrome.find_element_by_id('tbc_window_iframe_19'))
        time.sleep(5)
        my_course = WebDriverWait(chrome, 15, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#study-task')))
        my_course.click()
        studying = WebDriverWait(chrome, 15, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '#studyTaskPanel > div > div.filter-list.tbc-els-filter-list > dl:nth-child(2) > dd > span:nth-child(3)')))
        studying.click()

        try:
            last_page = int(chrome.find_element_by_class_name('pagnum-last').text)
        except:
            last_page = 1
        current_page = 1
        for i in range(1, last_page + 1):
            time.sleep(8)
            div = WebDriverWait(chrome, 15, 0.5).until(EC.presence_of_element_located((By.ID, 'studyTaskList')))
            section = WebDriverWait(div, 15, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#studyTaskList > section')))
            # section = div.find_element_by_css_selector('#studyTaskList > section')
            ul = section.find_element_by_tag_name('ul')
            li_list = ul.find_elements_by_tag_name('li')
            for li in li_list:
                single_class_div = WebDriverWait(li, 15, 0.5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'list-p')))
                class_name = single_class_div.find_element_by_tag_name('h3').text
                class_id = single_class_div.find_element_by_tag_name('h3').get_attribute('data-id')
                learn_detail = single_class_div.find_elements_by_class_name('learndetail')
                credit_hours = learn_detail[0].find_elements_by_tag_name('em')[0].text
                credit = learn_detail[0].find_elements_by_tag_name('em')[1].text
                em1 = learn_detail[1].find_elements_by_tag_name('em')[1]
                conditions_of_completion = em1.text
                learning_progress = learn_detail[1].find_element_by_tag_name('div').text.replace('\n', '').replace(' ', '')
                '''
                try:
                    learning_progress = re.match('课程学习(\d*)\%', learning_progress_text).group(1)
                except:
                    learning_progress = learning_progress_text
                '''
                print(class_name+','+class_id+','+credit+','+conditions_of_completion+','+learning_progress)
                f.write(class_name + ',')
                f.write(class_id + ',')
                f.write(credit + ',')
                f.write(conditions_of_completion + ',')
                f.write(learning_progress + '\n')
            if last_page > 1:
                if current_page < last_page:
                    # next_page = chrome.find_element_by_class_name('pag-next-page')
                    next_page = WebDriverWait(chrome, 30, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#LearningTaskPagination > div > div:nth-child(4) > button')))
                    next_page.click()
                    current_page += 1
                    time.sleep(3)


if __name__ == "__main__":
    login()
    find_courses_progress()
    chrome.quit()




