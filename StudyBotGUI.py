from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication, QRect, QMetaObject
from PyQt5.QtGui import QFont, QIcon
from sys import argv, exit
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from requests import post
from time import sleep, strftime, localtime, time
from json import loads
from re import findall

# 保存视频播放进度
save_progress_api = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveProgress.do"
# 同步刷新记录
update_time_api = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.updateTimestepByUserTimmer.do"
# 获取课程包含的小节信息
load_course_api = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.loadCourseItemTree.do"
# 选课接口，包含location信息
select_resource_api = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.selectResource.do?vbox_server=&fromNetWorkSetting=false"
# 确认选课接口
study_check_api_tmp = "http://study.foton.com.cn/els/html/coursestudyrecord/coursestudyrecord.studyCheck.do?courseId={}&scoId={}"
# 查看小节学习进度
scols_complate_api_tmp = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.scoIsComplate.do?courseId={}&processType=THREESCREEN"
# 单分屏获取播放进度api
one_screen_save_progress_api = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveCoursePrecent.do"
# 课程评估页面url模板
template_evaluation_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId={}&studyType=STUDY"
# 课程简介页面url模板
template_course_info_url = "http://study.foton.com.cn/els/html/course/course.courseInfo.do?courseId={}&p="
# 课后测试页面url模板
template_after_test_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId={}&studyType=STUDY"

course_id_list = []
cookie = {}
course_info_list = []
completed_list = []
video_id_list = []
video_name_list = []
course_url_list = []
course_name = ''
ONESCREEN = -1

header = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '140',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'study.foton.com.cn',
    'Origin': 'http://study.foton.com.cn',
    'Referer': 'http://study.foton.com.cn/els/flash/elnFlvPlayer.swf?v=4.0.2',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'}

data = {
        'courseId': '',
        'scoId': '',
        'progress_measure': '100',
        'session_time': '60:01',
        'location': '3601'
    }

data_single = {
    'courseId': '',
    'playTime': '9999'
}

select_video_data = {
    'courseId': '',
    'scoId': '',
    'firstLoad': 'true',
    'Location': '0',
    'elsSign': ''
}


class OpenBroswerThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(OpenBroswerThread, self).__init__()

    def run(self):
        self.signal.emit("正在打开登录页面，请登录后进入课程视频播放页面，回到程序选课\n")
        global driver
        driver = webdriver.Firefox(executable_path="./geckodriver.exe")
        # print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序继续执行")
        driver.get("http://study.foton.com.cn")
        driver.maximize_window()


class SelectCourseThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(SelectCourseThread, self).__init__()

    def run(self):
        """
        提取courseId
        """
        driver.switch_to.window(driver.window_handles[1])
        course_url_list.append(driver.current_url)
        course_id = findall(r"courseId=(.*)&vb_server=&", driver.current_url)[0]
        course_id_list.append(course_id)
        msg = "已选取{}门课".format(len(course_id_list))
        self.signal.emit(msg + '\n')


class StudyCousre(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(StudyCousre, self).__init__()

    def get_cookie(self):
        cookie_list = driver.get_cookies()
        for single_cookie in cookie_list:
            cookie[single_cookie['name']] = single_cookie['value']

    def show_time(self):
        cur_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        self.signal.emit(cur_time)
        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    def load_course(self, course_id):
        """
        加载课程信息，课程名称，视频名称，视频ID
        """
        global course_info_list
        global course_name

        try:
            loaded = post(load_course_api, headers=header, cookies=cookie,
                          data={'elsSign': cookie['eln_session_id'], 'courseId': course_id}, timeout=(15, 15))
        except:
            self.signal.emit("加载视频信息出错\n")
            # print("加载视频信息出错")
        else:
            if len(loaded.text) != 0:
                try:
                    course_info_orign = loads(loaded.text)
                except:
                    pass
                else:
                    course_name = course_info_orign[0]['text']
                    self.show_time()
                    self.signal.emit("课程名称是:《{}》，开始学习\n".format(course_name))
                    # print("课程名称是:《{}》，开始学习 ".format(course_name))
                    # 一部分在[0]['children']['0']['children']，另一部分课程在['0']['children']下

                    # print(course_info_orign[0]['children'][0]['children'])
                    # print(course_info_orign[0]['children'])

                    # if len(course_info_orign[0]['children'][0]['children']) == 1:
                    if len(course_info_orign[0]['children']) == 1:
                        if len(course_info_orign[0]['children'][0]['children']) == 1:
                            course_info_list = course_info_orign[0]['children']
                            c = True
                        else:
                            for sub_chapter in course_info_orign[0]['children'][0]['children']:
                                course_info_list.append(sub_chapter)
                            c = False
                    else:
                        for chapter in course_info_orign[0]['children']:
                            # course_info_list = course_info_orign[0]['children'][0]['children']
                            if len(chapter['children']) == 1:
                                course_info_list += chapter['children']
                            elif "id" in chapter:
                                course_info_list.append(chapter)
                            else:
                                for sub_chapter in chapter['children']:
                                    course_info_list.append(sub_chapter)
                        c = False
                    # print(course_info_list)

                    if not c:
                        for course_info in course_info_list:
                            # video_id_list是全局变量第二次学习时并不会覆盖第一次的id
                            if len(course_info["children"]) != 0:
                                for sub_course_info in course_info["children"]:
                                    video_id_list.append(sub_course_info['id'])
                                    video_name_list.append(sub_course_info['text'])
                            else:
                                video_id_list.append(course_info['id'])
                                video_name_list.append(course_info['text'])
                    else:
                        for course_info in course_info_list:
                            video_id_list.append(course_info['children'][0]['id'])
                            video_name_list.append(course_info['children'][0]['text'])
                    # print(video_id_list)
                    # print(video_name_list)

    def get_completed_video_list(self, course_id):
        """
        获取已经完成的视频列表
        """
        if ONESCREEN != 1:
            global completed_list
            scols_complate_api = scols_complate_api_tmp.format(course_id)
            try:
                c = post(scols_complate_api, headers=header, cookies=cookie,
                         data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
            except:
                self.signal.emit("获取视频完成列表出错\n")
                # print("获取视频完成列表出错")
            else:
                if len(c.text) != 0:
                    completed_list = loads(c.text)

    def select_video(self, course_id, video_id):
        global ONESCREEN
        if ONESCREEN != 1:
            select_video_data['courseId'] = course_id
            select_video_data['scoId'] = video_id
            select_video_data['elsSign'] = cookie['eln_session_id']
            post(select_resource_api, headers=header, cookies=cookie, data=select_video_data, timeout=(15, 15))
            study_check_api = study_check_api_tmp.format(course_id, video_id)
            post(study_check_api, headers=header, cookies=cookie, data={'elsSign': cookie['eln_session_id']},
                 timeout=(15, 15))

    def course_finished(self, course_id):
        """
        判断课程是否学习完毕
        """
        global ONESCREEN
        if ONESCREEN != 1:

            if len(completed_list) == len(video_id_list):
                return True
            else:
                return False
        else:
            data_single['courseId'] = course_id
            try:
                sr = post(one_screen_save_progress_api, headers=header, cookies=cookie, data=data_single, timeout=(15, 15))
            except:
                self.signal.emit("获取进度失败")
            else:
                sr_data = sr.text
                if len(sr_data) != 0:
                    try:
                        sr_dict = loads(sr_data)
                    except:
                        # print("HTTP Status 500  服务器内部错误")
                        pass
                    else:
                        if 'courseProgress' in sr_dict:
                            if sr_dict['courseProgress'] == '100':
                                return True
                            else:
                                return False
                        else:
                            return False

    def video_finished(self, course_id, video_id, video_name):
        """
        判断视频是否播放完毕
        """
        global course_name
        data['courseId'] = course_id
        data['scoId'] = video_id
        self.get_completed_video_list(course_id)

        # print(course_id)
        # print(video_id)
        # print(completed_list)

        if video_id in completed_list:
            return True
        try:
            r = post(save_progress_api, headers=header, cookies=cookie, data=data, timeout=(15, 15))
        except:
            self.signal.emit("获取视频播放进度时出错\n")
            # print("获取视频播放进度时出错")
        else:
            r_data = r.text
            # print(r.text)
            if len(r_data) != 0:
                # print(r_data)
                try:
                    r_dict = loads(r_data)
                except:
                    self.signal.emit("HTTP Status 500  服务器内部错误\n")
                    # print("HTTP Status 500  服务器内部错误")
                else:
                    if 'completed' in r_dict:
                        if r_dict['completed'] == 'true':
                            return True
                        else:
                            self.show_time()
                            self.signal.emit("{} 视频播放进度{}%，《{}》课程学习进度{}%\n".format(video_name,
                                r_dict['completeRate'], course_name, r_dict['courseProgress']))
                            # print("视频播放进度{}%，课程学习进度{}%".format(r_dict['completeRate'], r_dict['courseProgress']))
                            return False
                    else:
                        return False
            else:
                return False

    def course_evaluation(self, course_id):
        global course_name
        evaluation_url = template_evaluation_url.format(course_id)

        def do_evaluation():
            driver.switch_to.window(driver.window_handles[1])
            span = WebDriverWait(driver, 15, 0.5).until(EC.presence_of_element_located((By.ID, 'star')))
            a_list = span.find_elements_by_tag_name('a')
            a_list[4].click()
            form_choice = WebDriverWait(driver, 15, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'form_choice')))
            question_list = form_choice.find_elements_by_tag_name("div")
            for question in question_list[:-1]:
                p_list = question.find_elements_by_tag_name("p")
                p6 = p_list[1]
                input_button = p6.find_element_by_tag_name("input")
                input_button.click()
            q5 = question_list[-1]
            textarea = q5.find_element_by_tag_name("textarea")
            textarea.click()
            textarea.send_keys("听君一席话，胜读十年书！")
            submit = driver.find_element_by_id("courseEvaluateSubmit")
            submit.click()
            table = driver.find_element_by_id("button0ButtonPanel")
            table.click()
            view = driver.find_element_by_id("courseEvaluateViewBtn")
            view.click()
            sleep(1)

        def evaluation():
            driver.switch_to.window(driver.window_handles[1])
            try:
                studyProgress = WebDriverWait(driver, 15, 0.5).until(
                    EC.presence_of_element_located((By.ID, "studyProgress"))
                )
                score = studyProgress.text
                if score == "100":
                    # 学完了，可以开始评估
                    courseStudyCourseGoNext = driver.find_element_by_id("courseStudyCourseGoNext")
                    courseStudyCourseGoNext.click()
                    sleep(6)
                    do_evaluation()
            except:
                do_evaluation()

        driver.get(evaluation_url)
        sleep(4)
        self.show_time()
        self.signal.emit("课程《{}》评估开始\n".format(course_name))
        try:
            evaluation()
        except:
            self.show_time()
            self.signal.emit("课程《{}》评估失败\n".format(course_name))
        else:
            self.show_time()
            self.signal.emit("课程《{}》评估完成\n".format(course_name))

    def course_quiz(self, course_id):
        global course_name
        course_info_url = template_course_info_url.format(course_id)
        driver.switch_to.window(driver.window_handles[1])
        driver.get(course_info_url)
        sleep(3)
        td_conditions_of_completion = WebDriverWait(driver, 15, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/table/tbody/tr[4]/td")))

        def do_quiz():
            questions_list = []
            correct_answers_list = []

            try:
                # 弹出提示框：考试时间还剩5分钟，抓紧时间。需要点确定
                abcenter_inner = driver.find_element_by_class_name("abcenter_inner")
                table = abcenter_inner.find_element_by_tag_name("div").find_element_by_tag_name("table")
                confirm_button = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[
                    1].find_elements_by_tag_name("td")[1].find_element_by_tag_name("input")
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
                        self.show_time()
                        self.signal.emit("正在进行第一次课后测试\n")
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
                        print(p.text)
                        if float(score) >= 80:
                            # 运气好，一次通过课后测试，点查看结果
                            self.signal.emit("课程《{}》第一次课后测试通过，获得{}分\n".format(course_name, score))
                            div = message.find_elements_by_tag_name("div")[1]
                            courseExamMsgViewBtn = div.find_element_by_id("courseExamMsgViewBtn")
                            courseExamMsgViewBtn.click()
                            sleep(6)
                        else:
                            # 点查看结果，记录答案
                            self.show_time()
                            self.signal.emit("很遗憾，课程《{}》第一次课后测试失败，获得{}分，还有1次补考机会，开始记录答案\n".format(course_name, score))
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
                                # self.signal.emit("正在记录第{}题答案".format(j + 1))

                                # 还得去掉题目前的序号和点
                                answers_text_list = []
                                original_question_list = question_item.find_element_by_class_name(
                                    "choice_tit").text.split(" ")[1:]
                                question = ""
                                for x, q in enumerate(original_question_list):
                                    question = question + q
                                    if x < len(original_question_list) - 1:
                                        question = question + " "
                                questions_list.append(question)

                                self.signal.emit("第{}题题目是【{}】".format(j+1, question))

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
                                        answer_text = choice.find_element_by_tag_name(
                                            "span").find_element_by_tag_name("label").text
                                        self.signal.emit("第{}题正确答案是【{}】\n".format(j+1, answer_text))
                                        answers_text_list.append(answer_text)

                                print(answers_text_list)

                                # question_text_list.append({question: answers_text_list})
                                correct_answers_list.append(answers_text_list)
                            sleep(4)
                            makeup_exam = driver.find_element_by_class_name(
                                "from_confirm").find_element_by_tag_name("button")
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
                                self.show_time()
                                self.signal.emit("正在补考第{}题".format(k + 1))
                                sleep(0.5)
                                show = 1
                                original_makeup_question_text_list = makeup_question_item.find_element_by_class_name(
                                    "choice_tit").text.split(" ")[1:]
                                makeup_question_text = ""
                                for x, q in enumerate(original_makeup_question_text_list):
                                    makeup_question_text = makeup_question_text + q
                                    if x < len(original_makeup_question_text_list) - 1:
                                        makeup_question_text = makeup_question_text + " "

                                self.signal.emit("补考题目是：【{}】".format(makeup_question_text))

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

                                            self.signal.emit("正确答案是：【{}】\n".format(answer))
                                else:
                                    self.signal.emit("该题目【{}】 在第一次测试时未出现，没有记录正确答案\n".format(makeup_question_text))
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
                                self.show_time()
                                self.signal.emit("课程《{}》课后测试通过，获得{}分\n".format(course_name, makeup_score))
                    else:
                        # 这是第二次考试，无法找到答案，请手工考试
                        self.show_time()
                        self.signal.emit("这是第二次考试，无法记录答案，请在答题结束后重新学习")
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
                else:
                    # 不在课后测试页面
                    pass
        if td_conditions_of_completion.text == "课后测试":
            after_test_url = template_after_test_url.format(course_id)
            driver.switch_to.window(driver.window_handles[1])
            driver.get(after_test_url)
            sleep(6)
            do_quiz()


    def clear_list(self):
        video_id_list.clear()
        video_name_list.clear()
        completed_list.clear()
        course_info_list.clear()

    def print_list(self):
        print(video_id_list)
        print(video_name_list)
        print(completed_list)
        print(course_info_list)

    def run(self):
        global course_name, ONESCREEN
        for i, course_url in enumerate(course_url_list):
            self.show_time()
            self.signal.emit("开始学习第{}门课\n".format(i+1))
            driver.get(course_url)
            course_id = course_id_list[i]
            # print(course_id)
            try:
                # ele存在说明是双分屏或者三分屏
                # ele = driver.find_element_by_id('vodtree')
                ele = WebDriverWait(driver, 5, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'vodtree')))
            except:
                ONESCREEN = 1
            else:
                ONESCREEN = 0
            div = WebDriverWait(driver, 5, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'barleft')))
            if ONESCREEN == 1:
                course_name = div.text.strip("网络设置")
            else:
                course_name = div.text
            self.get_cookie()
            self.load_course(course_id)
            self.get_completed_video_list(course_id)
            if self.course_finished(course_id):
                self.show_time()
                self.signal.emit("《{}》课程全部视频学习完毕\n".format(course_name))
                # print("《{}》课程全部视频学习完毕".format(course_name))
                self.clear_list()
                continue
            else:
                for j, video_id in enumerate(video_id_list):
                    video_name = video_name_list[j]
                    self.show_time()
                    self.signal.emit("开始学习 {} 视频\n".format(video_name))
                    # print("开始学习 {} 视频".format(video_name))
                    self.select_video(course_id, video_id)
                    while True:
                        if self.video_finished(course_id, video_id, video_name):
                            self.show_time()
                            self.signal.emit("{} 视频学习完毕\n".format(video_name))
                            # print("{} 视频学习完毕".format(video_name))
                            break
                        else:
                            post(update_time_api, headers=header, cookies=cookie,
                                 data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
                            sleep(180)
                    self.get_completed_video_list(course_id)
                    if self.course_finished(course_id):
                        self.show_time()
                        self.signal.emit("《{}》课程全部视频学习完毕\n".format(course_name))
                        # print("《{}》课程全部视频学习完毕".format(course_name))
                        self.clear_list()
                    sleep(1)
                self.clear_list()
            sleep(1)
            self.course_evaluation(course_id)
            self.course_quiz(course_id)
            ONESCREEN = -1
        course_id_list.clear()
        course_url_list.clear()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 750)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(20)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(20)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(20)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 788, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton.clicked.connect(self.open_broswer)
        self.pushButton_2.clicked.connect(self.select_course)
        self.pushButton_3.clicked.connect(self.study_course)
        self.cursor = self.textBrowser.textCursor()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "一键学习"))
        self.pushButton.setText(_translate("MainWindow", "开始学习"))
        self.pushButton_2.setText(_translate("MainWindow", "选这门课"))
        self.pushButton_3.setText(_translate("MainWindow", "选课结束\n一键学习"))

    def open_broswer(self):
        self.thread = OpenBroswerThread()
        self.thread.signal.connect(self.set_text_broswer)
        self.thread.start()

    def set_text_broswer(self, text):
        # self.textBrowser.setText(text)
        self.textBrowser.append(text)
        self.textBrowser.moveCursor(self.cursor.End)

    def select_course(self):
        self.thread2 = SelectCourseThread()
        self.thread2.signal.connect(self.set_text_broswer)
        self.thread2.start()

    def study_course(self):
        self.thread3 = StudyCousre()
        self.thread3.signal.connect(self.set_text_broswer)
        self.thread3.start()


if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)
    app.setWindowIcon(QIcon(r"Images/foton.jpg"))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    exit(app.exec_())
