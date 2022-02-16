from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome = webdriver.Chrome()
chrome.implicitly_wait(10)
chrome.get("http://study.foton.com.cn")
chrome.maximize_window()
category_list = ['领导力学院', '工程学院', '制造学院', '营销学院', '金融学院', '其他专业课程', '国际学院', '通用类', '精品微课',
                 '计划类（面授）课程', '主题学习', '生产管理学院', '事业部专有课程', '研发管理学院', '市场运营学院', '财务管理学院',
                 '销售管理学院', '人力资源学院', '职业化学院', '领导力学院', '综合管理学院', '个人发展学院']


def login():
    account = input('请输入用户名：')
    password = input('请输入密码：')

    ele = chrome.find_element_by_id("loginName")
    ele.click()
    ele.send_keys(account)

    ele = chrome.find_element_by_id("password")
    ele.click()
    ele.send_keys(password)

    time.sleep(1)
    ele = chrome.find_element_by_css_selector("#fm1 > input.btn.btn-block.btn-primary.btn-lg")
    ele.click()


def find_courses_data():
    with open('course_data.txt', 'w', encoding='utf-8') as f:
        f.write('课程名称,')
        f.write('课程ID,')
        f.write('课程学分,')
        f.write('结业条件\n')
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
        chrome.switch_to.default_content()
        time.sleep(2)
        chrome.switch_to.frame(chrome.find_element_by_id('tbc_window_iframe_19'))
        time.sleep(2)
        for category in category_list:
            # ele = chrome.find_element_by_partial_link_text(category)
            ele = WebDriverWait(chrome, 15, 0.5).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, category)))
            ele.click()
            time.sleep(2)
            try:
                last_page = int(chrome.find_element_by_class_name('pagnum-last').text)
            except:
                last_page = 1
            for i in range(1, last_page+1):
                cp = 1
                # ele = chrome.find_element_by_id('categoryFilterResult')
                time.sleep(1)
                ele = WebDriverWait(chrome, 15, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'categoryFilterResult'))
                )
                # ul = ele.find_element_by_tag_name('ul')
                ul = WebDriverWait(ele, 15, 0.5).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'ul'))
                )
                # li_list = ul.find_elements_by_tag_name('li')
                li_list = WebDriverWait(ul, 15, 0.5).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'li'))
                )
                for li in li_list:
                    time.sleep(0.2)
                    # div = li.find_element_by_class_name('list-p')
                    div = WebDriverWait(li, 15, 0.5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'list-p')))
                    # h3 = div.find_element_by_tag_name('h3')
                    h3 = WebDriverWait(div, 15, 0.5).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'h3')))
                    course_name = h3.text
                    f.write(course_name + ',')
                    course_id = h3.get_attribute('data-id')
                    f.write(course_id + ',')
                    detial_list = div.find_elements_by_class_name('learndetail')
                    detial_credit = detial_list[0]
                    # 这里的credit是str类型
                    credit = detial_credit.find_elements_by_tag_name('span')[1].find_element_by_tag_name('em').text
                    f.write(credit)
                    f.write(',')
                    completion = div.find_element_by_class_name('coursebrief').find_element_by_tag_name('em').text
                    f.write(completion + '\n')
                if last_page > 1:
                    if cp < last_page:
                        # next_page = chrome.find_element_by_class_name('pag-next-page')
                        next_page = WebDriverWait(chrome, 30, 0.5).until(
                            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, '下一页')))
                        next_page.click()
                        cp += 1
                        time.sleep(3)


if __name__ == "__main__":
    login()
    find_courses_data()
    chrome.quit()




