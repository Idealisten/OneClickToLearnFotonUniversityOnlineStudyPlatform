# Response {"message":"操作成功！","status":"200","success":true,"jsonObj":null}
header = {
    #'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '140',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'study.foton.com.cn',
    'Origin': 'http://study.foton.com.cn',
    #'Referer': 'http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.learn.do?courseId=725f9cb55dfc42cea7e202a9567d4991&vb_server=&willGoStep=COURSE_COURSE_STUDY',
    'Referer':'http://study.foton.com.cn/els/flash/elnFlvPlayer.swf?v=4.0.2',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'}

data = {
    'courseId': 'b71db98d9b164c09a668528481c80005',
    'timeLimit':'noLimit',
    'startDate':'2020-03-19',
    'endDate':'2020-06-19'
}
cookie = {
    "JSESSIONID": "89F7E1C93E95A6670429688F1631F1B4",
    "corp_code": "foton",
    "nxYongdaoIp": "172.24.17.139",
    "eln_session_id": "elnSessionId.2d47a3e371e741f3a0b98f4254c3e556",
    #"learn_eln_session_id": "learn_eln_session_id.d64fc94024e241379307852c8277ebc2"
}

choose_url = 'http://study.foton.com.cn/els/html/courseCenter/courseCenter.chooseCourse.do'

r = post(choose_url, headers=header, cookies=cookie, data=data)

r.text