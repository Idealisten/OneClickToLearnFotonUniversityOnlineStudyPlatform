
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

template_after_test_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId={}&studyType=STUDY"


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
            qualification = line_list[-1]
            if credit == select_credit and qualification == "课后测试":
                course_info_list.append(line)
            line = f.readline()


def make_after_test(course_name):
    global success_num
    global fail_num
    try:
        # 弹出提示框：考试时间还剩5分钟，抓紧时间。需要点确定
        abcenter_inner = driver.find_element_by_class_name("abcenter_inner")
        table = abcenter_inner.find_element_by_tag_name("div").find_element_by_tag_name("table")
        confirm_button = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[1].find_elements_by_tag_name("td")[1].find_element_by_tag_name("input")
        confirm_button.click()
    except:
        # 点击确定后开始第一次做题
        courseInfoForm = driver.find_element_by_id("courseInfoForm")
        h1 = courseInfoForm.find_element_by_class_name("main_title")
        span = h1.find_element_by_tag_name("span")
        if span.text == "课后测试":
            # 在课后测试页面
            test_info = courseInfoForm.find_element_by_class_name("test_info")
            em_list = test_info.find_elements_by_tag_name("em")
            em = em_list[2]
            if em.text == "1":
                # 这是第一次考试,可以找到答案
                print("正在第一次测试")
                form_choice = courseInfoForm.find_element_by_class_name("form_choice")
                question_item_list = form_choice.find_elements_by_class_name("question-item")
                for i, question_item in enumerate(question_item_list):
                    print("正在做第{}题".format(i+1))
                    p_list = question_item.find_elements_by_tag_name("p")
                    span = p_list[1].find_element_by_tag_name("span")
                    choice = span.find_element_by_tag_name("input")
                    choice.click()
                from_confirm = driver.find_element_by_class_name("from_confirm")
                submit_button = from_confirm.find_element_by_id("goNext")
                submit_button.click()
                sleep(0.5)
                print("第一次测试已提交")
                # 提交后点查看结果
                message = driver.find_element_by_id("courseExamMsgBody")
                pointreson = message.find_element_by_class_name("pointreson")
                p = pointreson.find_element_by_tag_name("p")
                score = p.find_elements_by_tag_name("b")[0].text
                sleep(1)
                print("第一次测试的成绩是{}".format(score))
                print(p.text)
                if float(score) >= 60:
                    # 运气好，一次通过课后测试，点查看结果
                    div = message.find_elements_by_tag_name("div")[1]
                    courseExamMsgViewBtn = div.find_element_by_id("courseExamMsgViewBtn")
                    courseExamMsgViewBtn.click()
                    success_num += 1
                else:
                    # 进行补考，点查看结果，记录答案
                    print("开始记录答案")
                    div = message.find_elements_by_tag_name("div")[1]
                    courseExamMsgViewBtn = div.find_element_by_id("courseExamMsgViewBtn")
                    courseExamMsgViewBtn.click()
                    sleep(1)
                    # 点击查看结果按钮后跳转到展示答案页面，在此处记录答案
                    courseInfoForm = driver.find_element_by_id("courseInfoForm")
                    form_choice = courseInfoForm.find_element_by_class_name("form_choice")
                    question_item_list = form_choice.find_elements_by_class_name("question-item")
                    question_text_list = []
                    for j, question_item in enumerate(question_item_list):
                        print("正在记录第{}题答案".format(j+1))
                        sleep(0.5)
                        # 还得去掉题目前的序号和点
                        answers_text_list = []
                        question = question_item.find_element_by_class_name("choice_tit").text.split(" ")[-1]

                        print(question)

                        choice_list = question_item.find_elements_by_tag_name("p")[1:]
                        for c, choice in enumerate(choice_list):
                            sleep(0.5)
                            try:
                                image = choice.find_element_by_tag_name("img")
                            except:
                                # 没找到标记，这个选项不是正确答案
                                pass
                            else:
                                # 找到了，记录正确答案。题目顺序会变，选项顺序会变吗？
                                # answer_choice = choice.find_element_by_tag_name("span").find_element_by_tag_name("span").text
                                answer_text = choice.find_element_by_tag_name("span").find_element_by_tag_name("label").text
                                answers_text_list.append(answer_text)

                        print(answers_text_list)

                        question_text_list.append({question: answers_text_list})

                        print(question_text_list)

                    makeup_exam = driver.find_element_by_class_name("from_confirm").find_element_by_tag_name("button")
                    makeup_exam.click()
                    sleep(1)
                    print("开始补考")
                    courseInfoForm = driver.find_element_by_id("courseInfoForm")
                    form_choice = courseInfoForm.find_element_by_class_name("form_choice")
                    question_item_list = form_choice.find_elements_by_class_name("question-item")
                    for k, question_item in enumerate(question_item_list):
                        print("正在补考第{}题".format(k+1))
                        sleep(0.5)
                        show = 1
                        makeup_question_text = question_item.find_element_by_class_name("choice_tit").text.split(" ")[-1]

                        print("补考题目是： {}".format(makeup_question_text))

                        for i, question_text in enumerate(question_text_list):
                            sleep(0.2)
                            if makeup_question_text in question_text:
                                correct_answer_list = question_text_list[i].get(makeup_question_text)
                                choice_list = question_item.find_elements_by_tag_name("p")[1:]
                                for choice in choice_list:
                                    span = choice.find_element_by_tag_name("span")
                                    label = span.find_element_by_tag_name("label")
                                    answer = label.text
                                    if answer in correct_answer_list:
                                        label.click()
                                        sleep(0.2)

                                        print("正确答案是：{}".format(answer))

                            else:
                                show = 0
                                choice_list = question_item.find_elements_by_tag_name("p")[1:]
                                span = choice.find_element_by_tag_name("span")
                                label = span.find_element_by_tag_name("label")
                                label.click()
                                sleep(0.2)
                        if show == 0:
                            print("该题目 {} 在第一次测试时未出现，没有记录正确答案".format(makeup_question_text))
                    from_confirm = driver.find_element_by_class_name("from_confirm")
                    goNext = from_confirm.find_element_by_id("goNext")
                    goNext.click()
                    sleep(1)
                    courseExamMsgBody = driver.find_element_by_id("courseExamMsgBody")
                    pointreson = courseExamMsgBody.find_element_by_class_name("pointreson")
                    p = pointreson.find_element_by_tag_name("p")
                    print(course_name)
                    print(p.text)
                    makeup_score = p.find_element_by_tag_name("b").text
                    if float(makeup_score) >= 60:
                        success_num += 1
                        print("课程《{}》课后测试通过".format(course_name))
            else:
                # 这是第二次考试，无法找到答案，请手工考试
                print("这是第二次考试，无法记录答案，请手工考试")
                fail_num += 1
                fail_list.append(course_name)
        else:
            # 不在课后测试页面
            fail_num += 1
            fail_list.append(course_name)
            pass


def end_after_test():
    print("本次课后测试结束，共{}门课程".format(len(course_info_list)))
    print("通过{}门，未通过{}门".format(success_num, fail_num))
    if fail_num > 0:
        print("未通过的课程有{}".format(fail_list))
        print("请检查未通过的课程是否已经完成选课/学习/评估，未完成的课程无法课后测试。")


if __name__ == "__main__":
    print("课程学分：" + str(credit_list))
    select_credit = input("请输入要课后测试的课程的学分：")
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
            after_test_url = template_after_test_url.format(course_id)
            driver.get(after_test_url)
            sleep(1)
            print("正在课后测试《{}》课程".format(course_name))
            try:
                make_after_test(course_name)
            except:
                print("课程《{}》课后测试未通过".format(course_name))
                fail_num += 1
                fail_list.append(course_name)
        driver.quit()
        end_after_test()
