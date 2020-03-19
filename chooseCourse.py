# Response {"message":"操作成功！","status":"200","success":true,"jsonObj":null}
from selenium import webdriver
from requests import post
from selenium import webdriver
from time import sleep
from json import loads

success_num = 0

account = input("请输入用户名：")
password = input("请输入密码：")

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

sleep(1)

ele = driver.find_element_by_class_name('login_Btn')
ele.click()

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

cookie_list = driver.get_cookies()
cookie = {}
for single_cookie in cookie_list:
    cookie[single_cookie['name']] = single_cookie['value']

choose_url = 'http://study.foton.com.cn/els/html/courseCenter/courseCenter.chooseCourse.do'

r = post(choose_url, headers=header, cookies=cookie, data=data)

r_data = r.text
r_dict = loads(r_data)

if "success" in r_dict:
    if r_dict["success"]:
        success_num += 1
        print("选课成功!已经成功选课 {} 门".format(success_num))
