from selenium import webdriver
from requests import post
from time import sleep
from sys import stdout
from json import loads
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from email.mime.text import MIMEText
import smtplib

credit_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
               1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9,
               2, 2.4, 2.5, 2.6, 3, 3.5, 4, 4.4, 4.5,
               5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5,
               10, 11, 11.5, 12, 14.5, 15, 17.5]

fail_num = 0
success_num = 0
fail_list = []
course_info_list = []
course_id = ''
course_name = ''

header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '57',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'study.foton.com.cn',
        'Origin': 'http://study.foton.com.cn',
        'Referer': 'http://study.foton.com.cn/els/flash/elnFlvPlayer.swf?v=4.0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'}

data_single = {
    'courseId': 'PTC035903',
    'playTime': '9999'
}

data_double = {
    'courseId': ' ',
    'scoId': ' ',
    'progress_measure': '100'
}

select_video_data = {
    'courseId': '',
    'scoId': '',
    'firstLoad': 'true',
    'Location': '0',
    'elsSign': ''
}

cookie = {}

template_url = "http://study.foton.com.cn/els/html/coursestudyrecord/coursestudyrecord.studyCheck.do?courseId={}&scoId={}"
progress_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveProgress.do"
precent_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveCoursePrecent.do"
template_watch_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.learn.do?courseId={}&vb_server=&willGoStep=COURSE_COURSE_STUDY"
template_play_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId={}&studyType=STUDY"

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

def show_time():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def open_broswer():
    driver.implicitly_wait(10)
    driver.get("http://study.foton.com.cn")


def login():
    print("登录中...")
    usrname = driver.find_element_by_id('loginName')
    usrname.click()
    usrname.send_keys(username)

    passwd = driver.find_element_by_id('password')
    passwd.click()
    passwd.send_keys(password)

    sleep(2)

    ele = driver.find_element_by_class_name('login_Btn')
    ele.click()


def login_ok():
    if driver.current_url == "http://study.foton.com.cn/os/html/index.init.do":
        # 登录成功
        return True
    else:
        return False


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


def select_video(course_id, video_id):
    select_video_data['courseId'] = course_id
    select_video_data['scoId'] = video_id
    select_video_data['elsSign'] = cookie['eln_session_id']
    post(select_resource_api, headers=header, cookies=cookie, data=select_video_data, timeout=(15, 15))
    study_check_api = study_check_api_tmp.format(course_id, video_id)
    post(study_check_api, headers=header, cookies=cookie, data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))


def get_completed_video_list(course_id):
    """
    获取已经完成的视频列表
    """
    completed_list = []
    scols_complate_api = scols_complate_api_tmp.format(course_id)
    try:
        cmpls = post(scols_complate_api, headers=header, cookies=cookie,
                     data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
    except:
        print("获取视频完成列表出错")
    else:
        if len(cmpls.text) != 0:
            completed_list = loads(cmpls.text)
            return completed_list


def course_finished(completed_list, vid_list):
    """
    判断课程是否学习完毕
    """
    if len(completed_list) == len(vid_list):
        return True
    else:
        return False


def video_finished(course_id, video_id):
    """
    判断视频是否播放完毕
    """
    data_double['courseId'] = course_id
    data_double['scoId'] = video_id
    completed_list = get_completed_video_list(course_id)

    # print(course_id)
    # print(video_id)
    # print(completed_list)

    if video_id in completed_list:
        return True
    try:
        r = post(save_progress_api, headers=header, cookies=cookie, data=data_double, timeout=(15, 15))
    except:
        print("获取视频播放进度时出错")
    else:
        r_data = r.text

        # print(r.text)

        if len(r_data) != 0:

            # print(r_data)

            try:
                r_dict = loads(r_data)
            except:
                print("HTTP Status 500  服务器内部错误")
            else:
                if 'completed' in r_dict:
                    if r_dict['completed'] == 'true':
                        return True
                    else:
                        show_time()
                        print("视频播放进度{}%，课程学习进度{}%".format(
                            r_dict['completeRate'], r_dict['courseProgress']))
                        return False
                else:
                    return False
        else:
            return False


def pre_test():
    form = driver.find_element_by_id("coursePretestForm")
    try:
        h2 = form.find_element_by_tag_name("h2")
    except:
        form_choice = driver.find_element_by_class_name("form_choice")
        # choice_type_list = form_choice.find_elements_by_class_name("choice_type")
        # for choice_type in choice_type_list:
        # if choice_type.text == "判断题":
        # 判断题/选择题(单选，多选)都只需要循环点question-item的第一个选项就行了
        question_item_list = form_choice.find_elements_by_class_name("question-item")
        for question_item in question_item_list:
            p_list = question_item.find_elements_by_tag_name("p")
            span = p_list[1].find_element_by_tag_name("span")
            button = span.find_element_by_tag_name("input")
            button.click()
            sleep(0.1)
        from_confirm = driver.find_element_by_class_name("from_confirm")
        submit_button = from_confirm.find_element_by_id("coursePretestSubmit")
        submit_button.click()

        next_step = driver.find_element_by_id("upCoursePretestGoNextBtn")
        next_step.click()
        learn()
    else:
        if h2.text == "（无试题）":
            button = driver.find_element_by_class_name("from_confirm").find_element_by_tag_name("button")
            button.click()
            learn()


def is_finished():
    global success_num
    try:
        # 通过课程进度判断课程是否学习完成，span.text == '100'说明已经学完了
        # span = driver.find_element_by_id("studyProgress")
        span = WebDriverWait(driver, 3, 0.5).until(
            EC.presence_of_element_located((By.ID, 'studyProgress')))
    except:
        try:
            # 通过是否显示课程评估页面判断课程是否学习完成
            # h1 = driver.find_element_by_class_name("main_title")
            h1 = WebDriverWait(driver, 3, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'main_title')))
        except:
            # 不显示课程评估，没学完，开始学习
            learn()
        else:
            span = h1.find_element_by_tag_name('span')
            if span.text == "课程评估":
                success_num += 1

                print("恭喜你！课程《{}》 已经完成学习，已成功学习 {} 门".format(course_name, success_num))
                if success_num % 30 == 0:
                    info = "《{}》课程全部视频学习完毕.学习成功{}门.共{}门.学习进度{}".format(course_name, success_num,
                                                                       len(course_info_list),
                                                                       round(success_num / len(course_info_list),
                                                                             2))
                    msg = MIMEText(info, 'plain', 'utf-8')
                    server.sendmail(from_addr, [to_addr], msg.as_string())
            elif span.text == "课前测试":
                pre_test()
            elif span.text == "课后测试":
                success_num += 1
                print("恭喜你！课程《{}》 已经完成学习，已成功学习 {} 门".format(course_name, success_num))
                if success_num % 30 == 0:
                    info = "《{}》课程全部视频学习完毕.学习成功{}门.共{}门.学习进度{}".format(course_name, success_num,
                                                                       len(course_info_list),
                                                                       round(success_num / len(course_info_list),
                                                                             2))
                    msg = MIMEText(info, 'plain', 'utf-8')
                    server.sendmail(from_addr, [to_addr], msg.as_string())

    else:
        if span.text == '100':
            success_num += 1
            print("恭喜你！课程《{}》 已经完成学习，已成功学习 {} 门".format(course_name, success_num))
            if success_num % 30 == 0:
                info = "《{}》课程全部视频学习完毕.学习成功{}门.共{}门.学习进度{}".format(course_name, success_num,
                                                                   len(course_info_list),
                                                                   round(success_num / len(course_info_list),
                                                                         2))
                msg = MIMEText(info, 'plain', 'utf-8')
                server.sendmail(from_addr, [to_addr], msg.as_string())
        else:
            # 开始学习
            learn()


def get_cookie():
    cookie_list = driver.get_cookies()
    for single_cookie in cookie_list:
        cookie[single_cookie['name']] = single_cookie['value']


def learn():
    global success_num
    global fail_num
    play_button = WebDriverWait(driver, 3, 0.5).until(
        EC.presence_of_element_located((By.ID, 'courseRp_sel')))
    play_button.click()
    sleep(5)
    get_cookie()
    data_single['courseId'] = course_id
    data_double['courseId'] = course_id

    try:
        # ele存在说明是双分屏或者三分屏
        # ele = driver.find_element_by_id('vodtree')
        ele = WebDriverWait(driver, 3, 0.5).until(
            EC.presence_of_element_located((By.ID, 'vodtree')))
    except:
        # ele不存在说明是单分屏
        sleep(0.1)
        try:
            r = post(precent_url, headers=header, cookies=cookie, data=data_single, timeout=(15, 15))
        except:
            fail_num += 1
            print("课程《{}》学习失败，已学习失败{}门课程".format(course_name, fail_num))
            fail_list.append(course_name)
        else:
            r_data = r.text
            if len(r_data) != 0:
                r_dict = loads(r_data)
                if 'completed' in r_dict:
                    if r_dict['completed'] == 'true':
                        success_num += 1
                        print("恭喜你！课程《{}》 已经完成学习，已成功学习 {} 门".format(course_name, success_num))
                        if success_num % 30 == 0:
                            info = "《{}》课程全部视频学习完毕.学习成功{}门.共{}门.学习进度{}".format(course_name, success_num,
                                                                               len(course_info_list),
                                                                               round(success_num / len(course_info_list),
                                                                                     2))
                            msg = MIMEText(info, 'plain', 'utf-8')
                            server.sendmail(from_addr, [to_addr], msg.as_string())
            else:
                fail_num += 1
                print("课程《{}》学习失败，已学习失败{}门课程".format(course_name, fail_num))
                fail_list.append(course_name)
    else:
        # 双/三分屏
        completed_video_list = get_completed_video_list(course_id)
        vid_list = []
        title_list = []

        div_list = ele.find_elements_by_tag_name('div')
        for div in div_list[1:]:
            try:
                a = div.find_element_by_tag_name('a')
            except :
                pass
            else:
                video_id = a.get_attribute('data-id')
                vid_list.append(video_id)
                video_title = a.get_attribute('title')
                title_list.append(video_title)
                print("正在爬取 {} 视频数据...".format(video_title))
                stdout.flush()

        print("课程《{}》所有视频数据爬取完成！开始学习".format(course_name))
        if course_finished(completed_video_list, vid_list):
            show_time()
            print("《{}》课程全部视频学习完毕".format(course_name))
            success_num += 1
            if success_num % 30 == 0:
                info = "《{}》课程全部视频学习完毕.学习成功{}门.共{}门.学习进度{}".format(course_name, success_num, len(course_info_list),
                                                                   round(success_num / len(course_info_list), 2))
                msg = MIMEText(info, 'plain', 'utf-8')
                server.sendmail(from_addr, [to_addr], msg.as_string())
        else:
            for index, vid in enumerate(vid_list):
                sleep(1)
                video_title = title_list[index]
                data_double['scoId'] = vid
                video_url = template_url.format(course_id, vid)
                print("开始学习 {} 视频".format(video_title))
                select_video(course_id, vid)
                while True:
                    if video_finished(course_id, vid):
                        show_time()
                        print("{} 视频学习完毕".format(video_title))
                        sleep(1)
                        break
                    else:
                        post(update_time_api, headers=header, cookies=cookie,
                             data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
                        sleep(180)
                completed_video_list = get_completed_video_list(course_id)
                if course_finished(completed_video_list, vid_list):
                    show_time()
                    success_num += 1
                    print("《{}》课程全部视频学习完毕".format(course_name))
                    if success_num % 30 == 0:
                        info = "《{}》课程全部视频学习完毕.学习成功{}门.共{}门.学习进度{}".format(course_name, success_num, len(course_info_list), round(success_num/len(course_info_list), 2))
                        msg = MIMEText(info, 'plain', 'utf-8')
                        server.sendmail(from_addr, [to_addr], msg.as_string())
                        sleep(1)


def end_study():
    print("本次学习结束，共{}门课程".format(len(course_info_list)))
    print("学习成功{}门，学习失败{}门".format(success_num, fail_num))
    end_info = "本次学习结束，共{}门课程.学习成功{}门，学习失败{}门".format(len(course_info_list), success_num, fail_num)
    if fail_num > 0:
        print("学习失败的课程有{}".format(fail_list))
        print("请检查学习失败的课程是否已经完成选课，未进行选课的课程无法学习。")
    msg = MIMEText(end_info, 'plain', 'utf-8')
    server.sendmail(from_addr, [to_addr], msg.as_string())


if __name__ == "__main__":
    print("课程学分：" + str(credit_list))
    select_credit = input("请输入要学习的课程的学分：")
    if float(select_credit) not in credit_list:
        print("输入错误。告辞")
        exit(0)
    else:

        load_course()
        # driver = webdriver.Firefox()
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
        open_broswer()
        username = input("请输入用户名：")
        password = input("请输入密码：")
        from_addr = input("输入邮箱用户名")
        mail_password = input("输入邮箱密码或授权码")
        # 输入收件人地址:
        to_addr = input("输入收件人邮箱")
        # 输入SMTP服务器地址:
        smtp_server = input("输入SMTP服务器")
        server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
        server.set_debuglevel(1)
        server.login(from_addr, mail_password)
        login()
        while not login_ok():
            driver.refresh()
            sleep(2)
            login()
        print("登录成功")
        for c, course_info in enumerate(course_info_list):
            course_line_list = course_info.strip().split(',')
            course_id = course_line_list[-3]
            course_name = course_line_list[-4]
            play_url = template_play_url.format(course_id)
            driver.switch_to.window(driver.window_handles[0])
            driver.get(play_url)
            if c % 100 == 0:
                get_cookie()
            sleep(1)
            print("开始学习《{}》：".format(course_name))
            try:
                is_finished()
            except:
                fail_num += 1
                fail_list.append(course_name)
                print("请检查《{}》是否已选课！".format(course_name))
        driver.quit()
        server.quit()
        end_study()


