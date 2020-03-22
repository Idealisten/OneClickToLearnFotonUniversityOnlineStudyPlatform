# 必须把course_data.txt放在本程序同级目录下

from selenium import webdriver
from time import sleep
from json import loads
from requests import post

success_num = 0
fail_num = 0
all_num = 0
select_credit = 0
fail_list = []
course_info_list = []
course_id = ''
course_name = ''

header = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Length': '140',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'study.foton.com.cn',
    'Origin': 'http://study.foton.com.cn',
    # 'Referer': 'http://study.foton.com.cn/els/flash/elnFlvPlayer.swf?v=4.0.2',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'}

answers_list = [
    {"name": "e4426eaa0d5a4c1083d29ace0820de65", "value": "8b6a6126e61f42c5af591f4bcd34978f"},
    {"name": "b1c473cae233485999d6ef27e3a2bb45", "value": "9087518a9af74bd48958fbe20c8ba517"},
    {"name": "17b2460e37524b3780538fda99866349", "value": "8f53bb7fc2704057a86f9d75a658d9ea"},
    {"name": "25fb5a16f86b47ba84b4ef1e17bf4d7d", "value": "fc384c2c36d842d097920d7940dd449f"},
    {"name": "438c6e69477948f8a5e98465eaecfe7a", "value": "666"}]
data = {
    'courseId': 'b71db98d9b164c09a668528481c80005',
    'willGoStep': 'COURSE_EVALUATE',
    'answers': answers_list,
    'star': '5'
}

evaluate_url = "http://study.foton.com.cn/els/html/studyCourse/studyCourse.saveCourseEvaluate.do"

cookie = {}

credit_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
               1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9,
               2, 2.4, 2.5, 2.6, 3, 3.5, 4, 4.4, 4.5,
               5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5,
               10, 11, 11.5, 12, 14.5, 15, 17.5]


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


def get_cookie():
    cookie_list = driver.get_cookies()
    for single_cookie in cookie_list:
        cookie[single_cookie['name']] = single_cookie['value']


def judge():
    while True:
        ok = input("输入ok开始评估，输入no退出评估：")
        if ok == 'ok':
            break
        else:
            driver.quit()
            exit(0)


def evaluation():
    global success_num
    global fail_num
    try:
        r = post(evaluate_url, headers=header, cookies=cookie, data=data, timeout=(15, 15))
    except:
        fail_num += 1
        print("单分屏课程《{}》评估失败，已评估失败{}门课程".format(course_name, fail_num))
        fail_list.append(course_name)
        get_cookie()


def end_study():
    print("本次评估结束，共{}门课程".format(len(course_info_list)))
    print("评估成功{}门，评估失败{}门".format(success_num, fail_num))
    if fail_num > 0:
        print("评估失败的课程有{}".format(fail_list))
        print("请检查评估失败的课程是否已经完成学习，未学习完成或未选课的课程无法课程评估。")


if __name__ == "__main__":
    print("课程学分：" + str(credit_list))
    select_credit = input("请输入要评估的课程的学分：")
    if int(select_credit) not in credit_list:
        print("输入错误。告辞")
        exit(0)
    else:
        load_course()
        driver = webdriver.Firefox()
        open_broswer()
        judge()
        get_cookie()
        for course_info in course_info_list:
            course_line_list = course_info.strip().split(',')
            course_id = course_line_list[-3]
            course_name = course_line_list[-4]
            data['courseId'] = course_id
            evaluation()
        end_study()


