# Response {"message":"操作成功！","status":"200","success":true,"jsonObj":null}

# 必须把course_data.txt放在本程序同级目录下

from selenium import webdriver
from time import sleep
from json import loads
from requests import post

success_num = 0
fail_num = 0
all_num = 0
fail_list = []

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
    'courseId': 'b71db98d9b164c09a668528481c80005',
    'timeLimit': 'noLimit'
}

cookie = {}

credit_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
               1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9,
               2, 2.4, 2.5, 2.6, 3, 3.5, 4, 4.4, 4.5,
               5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5,
               10, 11, 11.5, 12, 14.5, 15, 17.5]

account = input("请输入用户名：")
password = input("请输入密码：")

print("课程学分：" + str(credit_list))
select_credit = input("请输入要选课的学分：")

if int(select_credit) not in credit_list:
    print("输入错误。告辞")
    exit(0)
else:
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()

    usrname = driver.find_element_by_id('loginName')
    usrname.click()
    usrname.send_keys(account)

    passwd = driver.find_element_by_id('password')
    passwd.click()
    passwd.send_keys(password)

    sleep(2)

    ele = driver.find_element_by_class_name('login_Btn')
    ele.click()

    while True:
        ok = input("进入主页后，输入ok开始选课，输入no退出选课：")
        if ok == 'ok':
            break
        else:
            driver.quit()
            exit(0)

    cookie_list = driver.get_cookies()
    for single_cookie in cookie_list:
        cookie[single_cookie['name']] = single_cookie['value']

    choose_url = 'http://study.foton.com.cn/els/html/courseCenter/courseCenter.chooseCourse.do'

    with open('./course_data.txt', 'r', encoding='utf-8') as f:
        line = f.readline()
        line = f.readline()
        while line:
            line_list = line.strip().split(',')
            completion = line_list[-1]
            credit = line_list[-2]
            course_id = line_list[-3]
            course_name = line_list[-4]
            if (completion != "课后测试") and (credit == select_credit):
                data['courseId'] = course_id
                all_num += 1
                try:
                    r = post(choose_url, headers=header, data=data, cookies=cookie, timeout=(15, 15))
                    sleep(1)
                    r_code = r.status_code
                except:
                    cookie_list = driver.get_cookies()
                    for single_cookie in cookie_list:
                        cookie[single_cookie['name']] = single_cookie['value']
                    print("《{}》课程选课失败".format(course_name))
                    fail_num += 1
                    fail_list.append(course_name)
                    sleep(3)
                else:
                    if r.status_code == 200:
                        r_data = r.text
                        r_dict = loads(r_data)
                        if "success" in r_dict:
                            if r_dict["success"]:
                                success_num += 1
                                print("《{}》选课成功!共选课成功 {} 门".format(course_name, success_num))
                            else:
                                print("《{}》课程选课失败".format(course_name))
                                fail_num += 1
                                fail_list.append(course_name)
                        else:
                            print("《{}》课程选课失败".format(course_name))
                            fail_num += 1
                            fail_list.append(course_name)
                    else:
                        print("《{}》课程选课失败".format(course_name))
                        fail_list.append(course_name)

            line = f.readline()

    print("\n")
    print("选课结束。")
    print("本次选课共有{}门课程".format(all_num))
    print("其中选课成功 {} 门".format(success_num))
    print("选课失败 {} 门".format(fail_num))
    if fail_num > 0:
        print("选课失败的课程有{}，请手动检查".format(fail_list))
    driver.quit()






