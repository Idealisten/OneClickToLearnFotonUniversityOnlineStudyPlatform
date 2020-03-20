from selenium import webdriver
from requests import post
from time import sleep
from sys import stdout
from json import loads
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium

credit_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
               1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9,
               2, 2.4, 2.5, 2.6, 3, 3.5, 4, 4.4, 4.5,
               5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5,
               10, 11, 11.5, 12, 14.5, 15, 17.5]

fail_num = 0
success_num = 0
select_credit = 0
success_study = 0
fail_study = 0
course_info_list = []
i = 1

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

template_url = "http://study.foton.com.cn/els/html/coursestudyrecord/coursestudyrecord.studyCheck.do?courseId={}&scoId={}"
progress_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveProgress.do"
precent_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveCoursePrecent.do"
template_watch_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.learn.do?courseId={}&vb_server=&willGoStep=COURSE_COURSE_STUDY"
template_play_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId={}&studyType=STUDY"

def open_broswer():
    global select_credit

    print("课程学分：" + str(credit_list))
    select_credit = input("请输入要选课的学分：")

    print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序输入ok继续执行")

    driver.implicitly_wait(10)
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()


def study():
    global select_credit
    global success_num
    global fail_num
    while True:
        ok = input("输入ok开始学习，输入no退出学习：")
        if ok == 'ok':
            break
        else:
            driver.quit()
            exit(0)
    driver.switch_to.window(driver.window_handles[1])

    global i
    with open('./course_data.txt', 'r', encoding='utf-8') as f:
        line = f.readline()
        line = f.readline()
        while line:
            course_info_list.append(line)
            line = f.readline()

    for course_info in course_info_list:
        sleep(0.1)
        line_list = course_info.strip().split(',')
        credit = line_list[-2]
        if credit == select_credit:
            course_id = line_list[-3]
            course_name = line_list[-4]
            play_url = template_play_url.format(course_id)
            driver.switch_to.window(driver.window_handles[1])
            driver.get(play_url)
            sleep(1)
            try:
                # try成功说明此门课已选课还未学习
                play_button = WebDriverWait(driver, 3, 0.5).until(EC.presence_of_element_located((By.ID, 'courseRp_sel')))
            except:
                # 否则说明已经学习完毕进入课程评估页面
                h1 = driver.find_element_by_class_name("main_title")
                span = h1.find_element_by_tag_name('span')
                if span.text == "课程评估":
                    print("恭喜你！单分屏课程《{}》 已经完成学习".format(course_name))
            else:
                # 如果还未学习则进入视频播放页面开始学习
                play_button.click()
                sleep(1)
                cookie_list = driver.get_cookies()
                cookie = {}
                for single_cookie in cookie_list:
                    cookie[single_cookie['name']] = single_cookie['value']

                data_single['courseId'] = course_id
                data_double['courseId'] = course_id
                vid_list = []
                title_list = []
                try:
                    # ele存在说明是双分屏或者三分屏
                    ele = driver.find_element_by_id('vodtree')
                except:
                    # ele不存在说明是单分屏
                    r = post(precent_url, headers=header, cookies=cookie, data=data_single, timeout=(15, 15))
                    r_data = r.text
                    r_dict = loads(r_data)
                    if r_dict is not None:
                        if 'completed' in r_dict:
                            if r_dict['completed'] == 'true':
                                print("恭喜你！单分屏课程《{}》 已经完成学习".format(course_name))
                                stdout.flush()
                                success_num += 1
                            else:
                                print("单分屏课程《{}》 学习失败".format(course_name))
                                fail_num += 1
                        else:
                            print("单分屏课程《{}》 学习失败".format(course_name))
                            fail_num += 1
                    else:
                        print("单分屏课程《{}》 学习失败".format(course_name))
                        fail_num += 1
                else:
                    div_list = ele.find_elements_by_tag_name('div')
                    for div in div_list[1:]:
                        try:
                            a = div.find_element_by_tag_name('a')

                        except BaseException:
                            pass
                        else:
                            video_id = a.get_attribute('data-id')
                            vid_list.append(video_id)
                            video_title = a.get_attribute('title')
                            title_list.append(video_title)
                            print("正在爬取 {} 视频数据...".format(video_title))
                            stdout.flush()
                    print("所有视频数据爬取完成！开始学习")

                    for index, vid in enumerate(vid_list):
                        title = title_list[index]
                        data_double['scoId'] = vid
                        video_url = template_url.format(course_id, vid)
                        post(video_url, headers=header, cookies=cookie,
                             data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
                        sleep(0.2)
                        r = post(progress_url, headers=header, cookies=cookie, data=data_double, timeout=(15, 15))
                        r_data = r.text
                        r_dict = loads(r_data)
                        if r_dict is not None:
                            if 'completed' in r_dict:
                                if r_dict['completed'] == 'true':
                                    print("{} 已经完成学习".format(title))
                                    stdout.flush()
                            if 'courseProgress' in r_dict:
                                if r_dict['courseProgress'] == "100":
                                    print("恭喜你！双分屏课程《{}》所有视频已学习完毕".format(course_name))
                                    success_num += 1
                                else:
                                    print("双分屏课程《{}》 学习失败".format(course_name))
                                    fail_num += 1
                            else:
                                print("双分屏课程《{}》 学习失败".format(course_name))
                                fail_num += 1
                        sleep(0.2)
    print("学习结束。学习成功{}门，学习失败{}门".format(success_num, fail_num))

    # c = post(video_url, headers=header, cookies=cookie)
    # print(c.status_code)


if __name__ == "__main__":
    driver = webdriver.Firefox()
    open_broswer()
    study()
    driver.quit()
