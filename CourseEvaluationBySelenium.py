# 特例 如何做好供应商开发与管理-供应商开发管理基本知识
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

course_info_list = []
fail_list = []
course_id = ''
course_name = ''
success_num = 0
fail_num = 0

credit_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
               1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9,
               2, 2.4, 2.5, 2.6, 3, 3.5, 4, 4.4, 4.5,
               5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5,
               10, 11, 11.5, 12, 14.5, 15, 17.5]

template_evaluation_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId={}&studyType=STUDY"


def judge():
    while True:
        ok = input("输入ok开始评估，输入no退出评估：")
        if ok == 'ok':
            break
        else:
            driver.quit()
            exit(0)


def open_broswer():
    print("正在打开登录页面，请登录后回到程序输入ok继续执行")
    driver.implicitly_wait(10)
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()


def load_course():
    global select_credit
    with open('./course_data.txt', 'r', encoding='utf-8') as f:
        line = f.readline()
        line = f.readline()
        while line:
            line_list = line.strip().split(',')
            credit = line_list[-2]
            if credit == select_credit:
                course_info_list.append(line)
            line = f.readline()


def evaluation():
    span = WebDriverWait(driver, 15, 0.5).until(EC.presence_of_element_located((By.ID, 'star')))
    a_list = span.find_elements_by_tag_name('a')
    a_list[4].click()
    form_choice = WebDriverWait(driver, 15, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'form_choice')))
    question_list = form_choice.find_elements_by_tag_name("div")
    for question in question_list[:4]:
        p_list = question.find_elements_by_tag_name("p")
        p6 = p_list[5]
        input_button = p6.find_element_by_tag_name("input")
        input_button.click()
    q5 = question_list[4]
    textarea = q5.find_element_by_tag_name("textarea")
    textarea.click()
    textarea.send_keys("666")
    submit = driver.find_element_by_id("courseEvaluateSubmit")
    submit.click()
    table = driver.find_element_by_id("button0ButtonPanel")
    table.click()
    view = driver.find_element_by_id("courseEvaluateViewBtn")
    view.click()
    sleep(0.5)


def end_evalustion():
    print("本次评估结束，共{}门课程".format(len(course_info_list)))
    print("评估成功{}门，评估失败{}门".format(success_num, fail_num))
    if fail_num > 0:
        print("评估失败的课程有{}".format(fail_list))
        print("请检查评估失败的课程是否已经完成选课/学习，未选课/学习的课程无法评估。")


if __name__ == "__main__":
    print("课程学分：" + str(credit_list))
    select_credit = input("请输入要评估的课程的学分：")
    if float(select_credit) not in credit_list:
        print("输入错误。告辞")
        exit(0)
    else:
        load_course()
        driver = webdriver.Firefox()
        open_broswer()
        judge()
        for course_info in course_info_list:
            course_line_list = course_info.strip().split(',')
            course_id = course_line_list[-3]
            course_name = course_line_list[-4]
            evaluation_url = template_evaluation_url.format(course_id)
            driver.get(evaluation_url)
            sleep(1)

            try:
                evaluation()
            except:
                print("课程《{}》评估失败".format(course_name))
                fail_num += 1
                fail_list.append(course_name)
            else:
                print("课程《{}》评估完成".format(course_name))
                success_num += 1
        driver.quit()
        end_evalustion()
