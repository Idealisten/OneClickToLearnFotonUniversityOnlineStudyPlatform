from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from re import findall

course_id_list = []
cookie = {}
course_info_list = []
completed_list = []
video_id_list = []
video_name_list = []
course_url_list = []
course_name = ''
template_after_test_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId={}&studyType=STUDY"

def open_broswer():
    print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序继续执行")
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()


def get_courseId():
    """
    提取courseId
    """
    driver.switch_to.window(driver.window_handles[1])
    course_url_list.append(driver.current_url)
    course_id = findall(r"courseId=(.*)&studyType=STUDY", driver.current_url)[0]
    course_id_list.append(course_id)


def select_course():
    """
    循环选课
    """
    while True:
        ok = input("输入ok选择当前课程，输入end结束选课，输入no退出：")
        if ok == 'ok':
            get_courseId()
        elif ok == 'end':
            print("选课结束，本次共选择了{}门课\n".format(len(course_id_list)))
            break
        else:
            print("告辞")
            driver.quit()
            exit(0)


def open_broswer():
    print("正在打开登录页面，请登录后回到程序输入ok继续执行")
    driver.implicitly_wait(10)
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()


def make_after_test():
    questions_list = []
    correct_answers_list = []
    try:
        # 弹出提示框：考试时间还剩5分钟，抓紧时间。需要点确定
        abcenter_inner = driver.find_element_by_class_name("abcenter_inner")
        table = abcenter_inner.find_element_by_tag_name("div").find_element_by_tag_name("table")
        confirm_button = \
        table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[1].find_elements_by_tag_name("td")[
            1].find_element_by_tag_name("input")
        confirm_button.click()
        sleep(1)
    except:
        # 点击确定后开始第一次做题
        sleep(5)
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
                print("正在第一次课后测试")
                form_choice = courseInfoForm.find_element_by_class_name("form_choice")
                question_item_list = form_choice.find_elements_by_class_name("question-item")
                for i, question_item in enumerate(question_item_list):
                    print("正在做第{}题".format(i + 1))
                    p_list = question_item.find_elements_by_tag_name("p")
                    span = p_list[1].find_element_by_tag_name("span")
                    choice = span.find_element_by_tag_name("input")
                    choice.click()
                    sleep(0.5)
                sleep(0.5)
                from_confirm = driver.find_element_by_class_name("from_confirm")
                submit_button = from_confirm.find_element_by_id("goNext")
                submit_button.click()
                sleep(3)
                print("第一次测试已提交")
                # 提交后点查看结果
                message = WebDriverWait(driver, 15, 1).until(
                    EC.presence_of_element_located((By.ID, "courseExamMsgBody"))
                )
                # message = driver.find_element_by_id("courseExamMsgBody")
                pointreson = message.find_element_by_class_name("pointreson")
                p = pointreson.find_element_by_tag_name("p")
                score = p.find_elements_by_tag_name("b")[0].text
                sleep(2)
                print("第一次测试的成绩是{}".format(score))
                print(p.text)
                if float(score) >= 60:
                    # 运气好，一次通过课后测试，点查看结果

                    div = message.find_elements_by_tag_name("div")[1]
                    courseExamMsgViewBtn = div.find_element_by_id("courseExamMsgViewBtn")
                    courseExamMsgViewBtn.click()
                    sleep(10)

                else:
                    # 点查看结果，记录答案
                    print("开始记录答案")
                    div = message.find_elements_by_tag_name("div")[1]
                    courseExamMsgViewBtn = div.find_element_by_id("courseExamMsgViewBtn")
                    courseExamMsgViewBtn.click()
                    sleep(1)
                    # 点击查看结果按钮后跳转到展示答案页面，在此处记录答案
                    courseInfoForm = driver.find_element_by_id("courseInfoForm")
                    form_choice = courseInfoForm.find_element_by_class_name("form_choice")
                    log_question_item_list = form_choice.find_elements_by_class_name("question-item")
                    question_text_list = []
                    for j, question_item in enumerate(log_question_item_list):
                        print("正在记录第{}题答案".format(j + 1))

                        # 还得去掉题目前的序号和点
                        answers_text_list = []
                        original_question_list = question_item.find_element_by_class_name("choice_tit").text.split(" ")[
                                                 1:]
                        question = ""
                        for x, q in enumerate(original_question_list):
                            question = question + q
                            if x < len(original_question_list) - 1:
                                question = question + " "
                        questions_list.append(question)

                        print(question)

                        choice_list = question_item.find_elements_by_tag_name("p")[1:]
                        for c, choice in enumerate(choice_list):

                            try:
                                image = choice.find_element_by_tag_name("img")
                            except:
                                # 没找到标记，这个选项不是正确答案
                                pass
                            else:
                                # 找到了，记录正确答案
                                # answer_choice = choice.find_element_by_tag_name("span").find_element_by_tag_name("span").text
                                answer_text = choice.find_element_by_tag_name("span").find_element_by_tag_name(
                                    "label").text
                                answers_text_list.append(answer_text)

                        print(answers_text_list)

                        # question_text_list.append({question: answers_text_list})
                        correct_answers_list.append(answers_text_list)
                    sleep(10)
                    makeup_exam = driver.find_element_by_class_name("from_confirm").find_element_by_tag_name("button")
                    makeup_exam.click()
                    sleep(10)
                    print("开始补考")
                    courseInfoForm = WebDriverWait(driver, 15, 1).until(
                        EC.presence_of_element_located((By.ID, "courseInfoForm"))
                    )
                    # courseInfoForm = driver.find_element_by_id("courseInfoForm")
                    form_choice = courseInfoForm.find_element_by_class_name("form_choice")
                    makeup_question_item_list = form_choice.find_elements_by_class_name("question-item")
                    for k, makeup_question_item in enumerate(makeup_question_item_list):
                        print("正在补考第{}题".format(k + 1))
                        sleep(0.5)
                        show = 1
                        original_makeup_question_text_list = makeup_question_item.find_element_by_class_name(
                            "choice_tit").text.split(" ")[1:]
                        makeup_question_text = ""
                        for x, q in enumerate(original_makeup_question_text_list):
                            makeup_question_text = makeup_question_text + q
                            if x < len(original_makeup_question_text_list) - 1:
                                makeup_question_text = makeup_question_text + " "

                        print("补考题目是： {}".format(makeup_question_text))

                        if makeup_question_text in questions_list:
                            index = questions_list.index(makeup_question_text)
                            correct_answer_list = correct_answers_list[index]
                            makeup_choice_list = makeup_question_item.find_elements_by_tag_name("p")[1:]
                            for makeup_choice in makeup_choice_list:
                                span = makeup_choice.find_element_by_tag_name("span")
                                label = span.find_element_by_tag_name("label")
                                answer = label.text
                                if answer in correct_answer_list:
                                    label.click()
                                    sleep(0.2)

                                    print("正确答案是：{}".format(answer))
                        else:
                            print("该题目 {} 在第一次测试时未出现，没有记录正确答案".format(makeup_question_text))
                            makeup_choice_list = makeup_question_item.find_elements_by_tag_name("p")[1:]
                            # 随便选一个B
                            makeup_choice = makeup_choice_list[1]
                            span = makeup_choice.find_element_by_tag_name("span")
                            label = span.find_element_by_tag_name("label")
                            label.click()
                            sleep(0.2)

                    from_confirm = driver.find_element_by_class_name("from_confirm")
                    goNext = from_confirm.find_element_by_tag_name("input")
                    goNext.click()
                    sleep(10)
                    courseExamMsgBody = WebDriverWait(driver, 15, 1).until(
                        EC.presence_of_element_located((By.ID, "courseExamMsgBody"))
                    )
                    # courseExamMsgBody = driver.find_element_by_id("courseExamMsgBody")
                    pointreson = courseExamMsgBody.find_element_by_class_name("pointreson")
                    p = pointreson.find_element_by_tag_name("p")
                    print(course_name)
                    print(p.text)
                    makeup_score = p.find_element_by_tag_name("b").text
                    if float(makeup_score) >= 60:
                        print("通过")
            else:
                # 这是第二次考试，无法找到答案，请手工考试
                print("这是第二次考试，无法记录答案，请手工考试")
        else:
            # 不在课后测试页面
            pass


if __name__ == "__main__":
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    open_broswer()
    select_course()
    for course_id in course_id_list:
        after_test_url = template_after_test_url.format(course_id)
        driver.get(after_test_url)
        sleep(1)
        try:
            make_after_test()
        except:
            pass
    driver.quit()


