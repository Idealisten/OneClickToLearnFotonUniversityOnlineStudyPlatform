from selenium import webdriver
from re import findall
from requests import post
from time import sleep
from sys import stdout
from os.path import exists


def open_broswer():
    print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序输入ok继续执行")

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get("http://study.foton.com.cn")
    driver.maximize_window()
    return driver


def login(driver, account, password):

    usrname = driver.find_element_by_id('loginName')
    usrname.click()
    usrname.send_keys(account)

    passwd = driver.find_element_by_id('password')
    passwd.click()
    passwd.send_keys(password)

    ele = driver.find_element_by_class_name('login_Btn')
    ele.click()

    sleep(5)


def study(driver, label):

    driver.switch_to.window(driver.window_handles[1])
    handles = driver.window_handles
    for handle in handles[1:]:

        driver.switch_to.window(handle)
        course_id = findall(r"courseId=(.*)&vb_server=&", driver.current_url)[0]

        cookie_list = driver.get_cookies()

        ele = driver.find_element_by_id('vodtree')
        div_list = ele.find_elements_by_tag_name('div')

        course_name = div_list[0].find_element_by_tag_name(
            'span').get_attribute('title')
        print("课程名称是:《{}》\n".format(course_name))

        vid_list = []
        title_list = []

        for div in div_list[1:]:
            try:
                a = div.find_element_by_tag_name('a')
                video_id = a.get_attribute('data-id')
                vid_list.append(video_id)
                video_title = a.get_attribute('title')
                title_list.append(video_title)
                if a is not None:
                    print("正在爬取 {} 视频数据...".format(video_title))
                    stdout.flush()
            except BaseException:
                pass

        print("所有视频数据爬取完成！开始学习")

        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '57',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'study.foton.com.cn',
            'Origin': 'http://study.foton.com.cn',
            'Referer': 'http://study.foton.com.cn/els/flash/elnFlvPlayer.swf?v=4.0.2',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}

        data = {
            'courseId': 'PTC035903',
            'scoId': 'sco_269c4374053d49e7b2661060addbf8b8',
            'progress_measure': '100'
        }

        template_url = "http://study.foton.com.cn/els/html/coursestudyrecord/coursestudyrecord.studyCheck.do?courseId={}&scoId={}"
        progress_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveProgress.do"

        cookie = {}
        for single_cookie in cookie_list:
            cookie[single_cookie['name']] = single_cookie['value']

        data['courseId'] = course_id

        for index, vid in enumerate(vid_list):
            title = title_list[index]
            data['scoId'] = vid
            video_url = template_url.format(course_id, vid)
            post(video_url, headers=header, cookies=cookie,
                 data={'elsSign': cookie['eln_session_id']})
            sleep(1)
            r = post(progress_url, headers=header, cookies=cookie, data=data)
            r_data = r.text
            r_dict = eval(r_data)
            if r_dict is not None:
                if 'completed' in r_dict:
                    if r_dict['completed'] == 'true':
                        print("{} 已经完成学习".format(title))
                        stdout.flush()
            sleep(0.2)

        print("恭喜你！{}课程所有视频已学习完毕".format(course_name))


def main():
    while True:
        print(
            "Attention! The author is not responsible for the consequences of running this script. \nIf you agree and continue running, please enter 'yes', if you do not agree, please enter 'no' to exit.")
        yes = input("Please enter your choice:")
        if yes == "yes":
            print("You have agreed. Program continues execution...")
            break
        else:
            print("You have refused. Goodbye~")
            exit(0)

    while True:
        print("请选择模式：1.普通模式 2.学霸模式 3.终极模式")
        label = input("请输入：")
        if label in ['1', '2', '3']:
            break
        else:
            print('输入错误，告辞')
            exit(0)

    if label != '3':
        account = input("请输入用户名:")
        password = input("请输入密码:")

    elif label == '3':
        if exists(r'./data.txt'):
            with open(r'./data.txt', 'r', encoding='utf-8') as f:
                account = f.readline().strip()
                password = f.readline().strip()
        else:
            account = input("请输入用户名:")
            password = input("请输入密码:")
            with open(r'./data.txt', 'w', encoding='utf-8') as f:
                f.write(account + '\n')
                f.write(password + '\n')

    driver = open_broswer()
    login(driver, account, password)
    while True:
        ok = input("输入ok开始学习，输入no退出学习：")
        if ok == 'ok':
            print("ok，程序继续，准备学习")
            try:
                study(driver, label)
            except:
                if label == '1':
                    print("发生未知错误，请确认该课程是否可以播放？告辞")
                    break
                else:
                    print("该课程无法播放，请切换课程")
        elif ok == 'no':
            print("你已退出程序")
            break
        else:
            print("输入错误，重新输入")
    driver.quit()


if __name__ == "__main__":
    main()





