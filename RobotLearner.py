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

course_id_list = []
cookie = []
course_info_list = []
completed_list = []
video_id_list = []
video_name_list = []
course_url_list = []

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
        'progress_measure': '100'
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
        elif ok == 'no':
            print("选课结束，本次共选择了{}门课".format(len(course_id_list)))
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


def load_course(course_id):
    """
    加载课程信息，课程名称，视频名称，视频ID
    """
    global course_info_list
    loaded = post(load_course_api, headers=header, cookies=cookie,
                  data={'elsSign': cookie['eln_session_id'], 'courseId': course_id})
    course_info_orign = loads(loaded.text)
    course_name = course_info_orign[0]['text']
    print("课程名称是:《{}》\n".format(course_name))
    course_info_list = course_info_orign[0]['children'][0]['children']
    for course_info in course_info_list:
        video_id_list.append(course_info['id'])
        video_name_list.append(course_info['text'])


def get_completed_video_list(course_id):
    """
    获取已经完成的视频列表
    """
    global completed_list
    scols_complate_api = scols_complate_api_tmp.format(course_id)
    c = post(scols_complate_api, headers=header, cookies=cookie,
             data={'elsSign': cookie['eln_session_id']})
    completed_list = loads(c.text)


def course_finished():
    """
    判断课程是否学习完毕
    """
    if len(completed_list) == len(course_info_list):
        return True
    else:
        return False


def video_finished():
    """
    判断视频是否播放完毕
    """
    r = post(save_progress_api, headers=header, cookies=cookie, data=data)
    r_data = r.text
    r_dict = loads(r_data)
    if r_dict is not None:
        if r_dict['completed'] == 'true':
            return True
        else:
            return False
    else:
        return False


def study():
    select_course()
    for i, course_url in enumerate(course_url_list):
        driver.get(course_url)
        course_id = course_id_list[i]
        get_cookie()
        load_course(course_id)
        get_completed_video_list()
        if course_finished():
            continue
        else:
            for j, video_id in enumerate(video_id_list):
                video_name = video_name_list[j]
                data['courseId'] = course_id
                data['scoId'] = video_id
                while True:
                    if video_finished():
                        # 进入下一个视频

                        break
                    else:
                        sleep(60)


if __name__ == "__main__":
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    open_broswer()