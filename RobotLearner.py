# 此挂机程序适用于无法秒课的三分屏课程
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests import post
from time import sleep
from json import loads
from re import findall
import time

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


def open_broswer():
    print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序继续执行")
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()


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


def get_courseId():
    """
    提取courseId
    """
    driver.switch_to.window(driver.window_handles[1])
    course_url_list.append(driver.current_url)
    course_id = findall(r"courseId=(.*)&vb_server=&", driver.current_url)[0]
    course_id_list.append(course_id)


def get_cookie():
    cookie_list = driver.get_cookies()
    for single_cookie in cookie_list:
        cookie[single_cookie['name']] = single_cookie['value']


def show_time():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def load_course(course_id):
    """
    加载课程信息，课程名称，视频名称，视频ID
    """
    global course_info_list
    global course_name

    try:
        loaded = post(load_course_api, headers=header, cookies=cookie,
                  data={'elsSign': cookie['eln_session_id'], 'courseId': course_id}, timeout=(15, 15))
    except:
        print("加载视频信息出错")
    else:
        if len(loaded.text) != 0:
            try:
                course_info_orign = loads(loaded.text)
            except:
                pass
            else:
                course_name = course_info_orign[0]['text']
                show_time()
                print("课程名称是:《{}》，开始学习 ".format(course_name))
                # 一部分在[0]['children']['0']['children']，另一部分课程在['0']['children']下

                # print(course_info_orign[0]['children'][0]['children'])
                # print(course_info_orign[0]['children'])

                # if len(course_info_orign[0]['children'] == 1) and len(course_info_orign[0]['children'][0]['children']) == 1:
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


def get_completed_video_list(course_id):
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
            print("获取视频完成列表出错")
        else:
            if len(c.text) != 0:
                completed_list = loads(c.text)


def select_video(course_id, video_id):
    global ONESCREEN
    if ONESCREEN != 1:
        select_video_data['courseId'] = course_id
        select_video_data['scoId'] = video_id
        select_video_data['elsSign'] = cookie['eln_session_id']
        post(select_resource_api, headers=header, cookies=cookie, data=select_video_data, timeout=(15, 15))
        study_check_api = study_check_api_tmp.format(course_id, video_id)
        post(study_check_api, headers=header, cookies=cookie, data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))


def course_finished(course_id):
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
            print("获取进度失败")
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


def video_finished(course_id, video_id):
    """
    判断视频是否播放完毕
    """
    data['courseId'] = course_id
    data['scoId'] = video_id
    get_completed_video_list(course_id)

    # print(course_id)
    # print(video_id)
    # print(completed_list)

    if video_id in completed_list:
        return True
    try:
        r = post(save_progress_api, headers=header, cookies=cookie, data=data, timeout=(15, 15))
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


def clear_list():
    video_id_list.clear()
    video_name_list.clear()
    completed_list.clear()
    course_info_list.clear()


def print_list():
    print(video_id_list)
    print(video_name_list)
    print(completed_list)
    print(course_info_list)


def study():
    global course_name, ONESCREEN
    select_course()
    for i, course_url in enumerate(course_url_list):
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
        get_cookie()
        load_course(course_id)
        get_completed_video_list(course_id)
        if course_finished(course_id):
            show_time()
            print("《{}》课程全部视频学习完毕".format(course_name))
            clear_list()
            continue
        else:
            for j, video_id in enumerate(video_id_list):
                video_name = video_name_list[j]
                show_time()
                print("开始学习 {} 视频".format(video_name))
                select_video(course_id, video_id)
                while True:
                    if video_finished(course_id, video_id):
                        show_time()
                        print("{} 视频学习完毕".format(video_name))
                        break
                    else:
                        post(update_time_api, headers=header, cookies=cookie,
                             data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
                        sleep(180)
                get_completed_video_list(course_id)
                if course_finished(course_id):
                    show_time()
                    print("《{}》课程全部视频学习完毕".format(course_name))
                    clear_list()
                sleep(1)
                ONESCREEN = -1
            clear_list()
        sleep(1)


if __name__ == "__main__":
    driver = webdriver.Firefox()
    # driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    open_broswer()
    study()
    driver.quit()
