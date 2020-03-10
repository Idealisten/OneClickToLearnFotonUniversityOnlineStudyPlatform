from selenium import webdriver
from re import findall
from json import dump

while True:
    print("Attention! The author is not responsible for the consequences of running this script. If you agree and continue running, please enter 'yes', if you do not agree, please enter 'no' to exit.")
    yes = input("Please enter your choice:")
    if yes == "yes":
        print("You have agreed. Program continues execution...")
        break
    else:
        print("You have refused. Goodbye~")
        exit(0)

print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序输入ok继续执行")

driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get("http://study.foton.com.cn")
driver.maximize_window()

while True:

    ok = input("请输入：")
    if ok == 'ok':
        print("ok，程序继续")
        break
    elif ok == 'no':
        print("你已退出程序")
        exit(0)
    else:
        print("输入错误，重新输入")

driver.switch_to.window(driver.window_handles[1])
course_id = findall(r"courseId=(.*)&vb_server=&", driver.current_url)[0]
with open('courseid.txt', 'w') as cr:
    cr.write(course_id)

cookie_list = driver.get_cookies()
with open('cookie.json', 'w') as ck:
    dump(cookie_list, ck)


ele = driver.find_element_by_id('vodtree')
div_list = ele.find_elements_by_tag_name('div')

course_name = div_list[0].find_element_by_tag_name('span').get_attribute('title')
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
    except:
        pass

with open('scoId.txt', 'w') as s:
    for vid in vid_list:
        s.write(vid)
        s.write('\n')

with open('title.txt', 'w') as t:
    for title in title_list:
        t.write(title)
        t.write('\n')

print("所有视频数据爬取完成！请执行gogogo.py")
