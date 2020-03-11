from requests import post
from time import sleep
from json import load
import json

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
    'X-Requested-With': 'XMLHttpRequest'
}

data = {
    'courseId': 'PTC035903',
    'scoId': 'sco_269c4374053d49e7b2661060addbf8b8',
    'progress_measure': '100'
}

template_url = "http://study.foton.com.cn/els/html/coursestudyrecord/coursestudyrecord.studyCheck.do?courseId={}&scoId={}"
progress_url = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveProgress.do"

video_id_list = []
video_title_list = []

with open('scoId.txt', 'r') as s:
    vid = s.readline().strip()
    while vid:
        video_id_list.append(vid)
        vid = s.readline().strip()

with open('title.txt', 'r') as t:
    title = t.readline().strip()
    while title:
        video_title_list.append(title)
        title = t.readline().strip()

with open('CourseID.txt', 'r') as co:
    courseid = co.readline()

with open('cookie.json', 'r') as ck:
    cookie_list = load(ck)
cookie = {}
for single_cookie in cookie_list:
    cookie[single_cookie['name']] = single_cookie['value']

data['courseId'] = courseid

for index, vid in enumerate(video_id_list):
    title = video_title_list[index]
    data['scoId'] = vid
    video_url = template_url.format(courseid, vid)
    post(video_url, headers=header, cookies=cookie, data={'elsSign': cookie['eln_session_id']})
    sleep(1)
    r = post(progress_url, headers=header, cookies=cookie, data=data)
    r_data = r.text
    r_dict = eval(r_data)
    if r_dict is not None:
        if r_dict['completed'] == 'true':
            print("{} 已经完成学习".format(title))
    sleep(1)
