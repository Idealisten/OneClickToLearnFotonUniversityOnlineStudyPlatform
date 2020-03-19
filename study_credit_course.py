from selenium import webdriver
from re import findall
from requests import post
from time import sleep
from sys import stdout

credit_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
               1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9,
               2, 2.4, 2.5, 2.6, 3, 3.5,4, 4.4, 4.5,
               5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5,
               10, 11, 11.5, 12, 14.5, 15, 17.5]

header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '57',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'study.foton.com.cn',
        'Origin': 'http://study.foton.com.cn',
        # 'Referer': 'http://study.foton.com.cn/els/flash/elnFlvPlayer.swf?v=4.0.2',
        # http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.learn.do?courseId=912eeb688b2444ce87a6717902120f42&vb_server=&willGoStep=COURSE_COURSE_STUDY
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'}

data = {
    'courseId': 'PTC035903',
    'playTime': '9999'
}

template_url = "http://study.foton.com.cn/els/html/coursestudyrecord/coursestudyrecord.studyCheck.do?courseId={}&scoId=null"
progress_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveCoursePrecent.do"


def open_broswer():
    print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序输入ok继续执行")

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()
    return driver


def study(driver):
    while True:
        ok = input("输入ok开始学习，输入no退出学习：")
        if ok == 'ok':
            break
        else:
            driver.quit()
            exit(0)
    driver.switch_to.window(driver.window_handles[1])

    cookie_list = driver.get_cookies()
    cookie = {}
    for single_cookie in cookie_list:
        cookie[single_cookie['name']] = single_cookie['value']

    # http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId=725f9cb55dfc42cea7e202a9567d4991&studyType=STUDY
    # course_id = findall(r"courseId=(.*)&studyType", driver.current_url)[0]
    print(credit_list)
    print("课程学分：" + str(credit_list))
    select_credit = input("请输入要选课的学分：")




    data['courseId'] = course_id

    ele = driver.find_element_by_class_name('info_tit')
    em = ele.find_element_by_tag_name('em')
    course_name = em.get_attribute('title')
    print("课程名称是:《{}》\n".format(course_name))

    video_url = template_url.format(course_id)
    # c = post(video_url, headers=header, cookies=cookie)
    # print(c.status_code)
    # 单视频课程不用打开视频页面，停留在“观看视频”按钮页面只发送一个学习进度post请求即可完成学习
    # “观看视频”按钮页面url http://study.foton.com.cn/els/html/studyCourse/studyCourse.enterCourse.do?courseId=725f9cb55dfc42cea7e202a9567d4991&studyType=STUDY
    r = post(progress_url, headers=header, cookies=cookie, data=data)
    print(r.status_code)
    r_data = r.text
    print(r_data)
    r_dict = eval(r_data)
    if r_dict is not None:
        if 'completed' in r_dict:
            if r_dict['completed'] == 'true':
                print("恭喜你！{} 已经完成学习".format(course_name))
                stdout.flush()
    else:
        print("该课程无法学习，请切换课程")
    driver.quit()


if __name__ == "__main__":
    study(open_broswer())

