
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
    # 弹出提示框：考试时间还剩5分钟，抓紧时间。需要点确定
    table = driver.find_element_by_id("button0ButtonPanel")
    confirm_button = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[1].find_elements_by_tag_name("td")[1].find_element_by_tag_name("input")
    confirm_button.click()
    # 点击确定后开始第一次做题
    courseInfoForm = driver.find_element_by_id("courseInfoForm")
    h1 = courseInfoForm.find_element_by_class_name("main_title")
    span = h1.find_elements_by_tag_name("span")
    if span.text == "课后测试":
        # 在课后测试页面
        test_info = courseInfoForm.find_element_by_class_name("test_info")
        em_list = test_info.find_elements_by_tag_name("em")
        em = em_list[2]
        if em.text == "1":
            # 这是第一次考试,可以找到答案
            form_choice = courseInfoForm.find_element_by_class_name("form_choice")
            question_item_list = form_choice.find_elements_by_class_name("question-item")
            for question_item in question_item_list:
                p_list = question_item.find_elements_by_tag_name("p")
                span = p_list[1].find_element_by_tag_name("span")
                choice = span.find_element_by_tag_name("input")
                choice.click()
            from_confirm = driver.find_element_by_class_name("from_confirm")
            submit_button = from_confirm.find_element_by_id("goNext")
            submit_button.click()
            # 提交后点查看结果
            message = driver.find_element_by_id("courseExamMsgBody")
            pointreson = message.find_element_by_class_name("pointreson")
            p = pointreson.find_element_by_tag_name("p")
            score = p.find_elements_by_tag_name("b")[0].text
            if float(score) >= 60:
                # 运气好，一次通过课后测试，点查看结果
                div = message.find_elements_by_tag_name("div")[1]
                courseExamMsgViewBtn = div.find_element_by_id("courseExamMsgViewBtn")
                courseExamMsgViewBtn.click()
            else:
                # 进行补考，点查看结果，记录答案
                div = message.find_elements_by_tag_name("div")[1]
                courseExamMsgViewBtn = div.find_element_by_id("courseExamMsgViewBtn")
                courseExamMsgViewBtn.click()
                # 点击查看结果按钮后跳转到展示答案页面，在此处记录答案
                courseInfoForm = driver.find_element_by_id("courseInfoForm")
                form_choice = courseInfoForm.find_element_by_class_name("form_choice")
                question_item_list = form_choice.find_elements_by_class_name("question-item")
                for question_item in question_item_list:
                    # 还得去掉题目前的序号和点
                    question = question_item.find_element_by_class_name("choice_tit").text
                    choice_list = question_item.find_elements_by_tag_name("p")[1:]
                    for c, choice in enumerate(choice_list):
                        try:
                            image = choice.find_element_by_tag_name("img")
                        except:
                            # 没找到标记，这个选项不是正确答案
                            pass
                        else:
                            # 找到了，记录正确答案。题目顺序会变，选项顺序会变吗？
                            answer_choice = choice.find_element_by_tag_name("span").find_element_by_tag_name("span").text
                            answer_text = choice.find_element_by_tag_name("span").find_element_by_tag_name("label").text



        else:
            # 这是第二次考试，无法找到答案，请手工考试
            pass
    else:
        # 不在课后测试页面
        pass


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

        end_evalustion()
