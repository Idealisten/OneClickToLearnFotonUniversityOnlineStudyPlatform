from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication, QRect, QMetaObject
from PyQt5.QtGui import QFont, QIcon
from sys import argv, exit
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from requests import post
from time import sleep, strftime, localtime, time
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
# 单分屏获取播放进度api
one_screen_save_progress_api = "http://study.foton.com.cn/els/html/courseStudyItem/courseStudyItem.saveCoursePrecent.do"

course_id_list = []
cookie = {}
course_info_list = []
completed_list = []
video_id_list = []
video_name_list = []
course_url_list = []
course_name = ''
ONESCREEN = -1

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
        'progress_measure': '100',
        'session_time': '60:01',
        'location': '3601'
    }

data_single = {
    'courseId': '',
    'playTime': '9999'
}

select_video_data = {
    'courseId': '',
    'scoId': '',
    'firstLoad': 'true',
    'Location': '0',
    'elsSign': ''
}


class OpenBroswerThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(OpenBroswerThread, self).__init__()

    def run(self):
        self.signal.emit("正在打开登录页面，请登录后进入课程视频播放页面，回到程序选课\n")
        global driver
        driver = webdriver.Firefox(executable_path="./geckodriver.exe")
        # print("正在打开登录页面，请登录后进入课程视频播放页面，然后回到程序继续执行")
        driver.get("http://study.foton.com.cn")
        driver.maximize_window()


class SelectCourseThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(SelectCourseThread, self).__init__()

    def run(self):
        """
        提取courseId
        """
        driver.switch_to.window(driver.window_handles[1])
        course_url_list.append(driver.current_url)
        course_id = findall(r"courseId=(.*)&vb_server=&", driver.current_url)[0]
        course_id_list.append(course_id)
        msg = "已选取{}门课".format(len(course_id_list))
        self.signal.emit(msg + '\n')


class StudyCousre(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(StudyCousre, self).__init__()

    def get_cookie(self):
        cookie_list = driver.get_cookies()
        for single_cookie in cookie_list:
            cookie[single_cookie['name']] = single_cookie['value']

    def show_time(self):
        cur_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        self.signal.emit(cur_time)
        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    def load_course(self, course_id):
        """
        加载课程信息，课程名称，视频名称，视频ID
        """
        global course_info_list
        global course_name

        try:
            loaded = post(load_course_api, headers=header, cookies=cookie,
                          data={'elsSign': cookie['eln_session_id'], 'courseId': course_id}, timeout=(15, 15))
        except:
            self.signal.emit("加载视频信息出错\n")
            # print("加载视频信息出错")
        else:
            if len(loaded.text) != 0:
                try:
                    course_info_orign = loads(loaded.text)
                except:
                    pass
                else:
                    course_name = course_info_orign[0]['text']
                    self.show_time()
                    self.signal.emit("课程名称是:《{}》，开始学习\n".format(course_name))
                    # print("课程名称是:《{}》，开始学习 ".format(course_name))
                    # 一部分在[0]['children']['0']['children']，另一部分课程在['0']['children']下

                    # print(course_info_orign[0]['children'][0]['children'])
                    # print(course_info_orign[0]['children'])

                    if len(course_info_orign[0]['children'][0]['children']) == 1:
                        course_info_list = course_info_orign[0]['children']
                        c = True
                    else:
                        course_info_list = course_info_orign[0]['children'][0]['children']
                        c = False
                    # print(course_info_list)

                    if not c:
                        for course_info in course_info_list:
                            # video_id_list是全局变量第二次学习时并不会覆盖第一次的id
                            video_id_list.append(course_info['id'])
                            video_name_list.append(course_info['text'])
                    else:
                        for course_info in course_info_list:
                            video_id_list.append(course_info['children'][0]['id'])
                            video_name_list.append(course_info['children'][0]['text'])
                    # print(video_id_list)
                    # print(video_name_list)

    def get_completed_video_list(self, course_id):
        """
        获取已经完成的视频列表
        """
        if ONESCREEN != 1:
            global completed_list
            scols_complate_api = scols_complate_api_tmp.format(course_id)
            try:
                c = post(scols_complate_api, headers=header, cookies=cookie,
                         data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
            except:
                self.signal.emit("获取视频完成列表出错\n")
                # print("获取视频完成列表出错")
            else:
                if len(c.text) != 0:
                    completed_list = loads(c.text)

    def select_video(self, course_id, video_id):
        select_video_data['courseId'] = course_id
        select_video_data['scoId'] = video_id
        select_video_data['elsSign'] = cookie['eln_session_id']
        post(select_resource_api, headers=header, cookies=cookie, data=select_video_data, timeout=(15, 15))
        study_check_api = study_check_api_tmp.format(course_id, video_id)
        post(study_check_api, headers=header, cookies=cookie, data={'elsSign': cookie['eln_session_id']},
             timeout=(15, 15))

    def course_finished(self, course_id):
        """
        判断课程是否学习完毕
        """
        global ONESCREEN
        if ONESCREEN != 1:

            if len(completed_list) == len(course_info_list):
                return True
            else:
                return False
        else:
            data_single['courseId'] = course_id
            try:
                sr = post(one_screen_save_progress_api, headers=header, cookies=cookie, data=data_single, timeout=(15, 15))
            except:
                self.signal.emit("获取进度失败")
            else:
                sr_data = sr.text
                if len(sr_data) != 0:
                    try:
                        sr_dict = loads(sr_data)
                    except:
                        # print("HTTP Status 500  服务器内部错误")
                        pass
                    else:
                        if 'courseProgress' in sr_dict:
                            if sr_dict['courseProgress'] == '100':
                                return True
                            else:
                                return False
                        else:
                            return False

    def video_finished(self, course_id, video_id, video_name):
        """
        判断视频是否播放完毕
        """
        global course_name
        data['courseId'] = course_id
        data['scoId'] = video_id
        self.get_completed_video_list(course_id)

        # print(course_id)
        # print(video_id)
        # print(completed_list)

        if video_id in completed_list:
            return True
        try:
            r = post(save_progress_api, headers=header, cookies=cookie, data=data, timeout=(15, 15))
        except:
            self.signal.emit("获取视频播放进度时出错\n")
            # print("获取视频播放进度时出错")
        else:
            r_data = r.text
            # print(r.text)
            if len(r_data) != 0:
                # print(r_data)
                try:
                    r_dict = loads(r_data)
                except:
                    self.signal.emit("HTTP Status 500  服务器内部错误\n")
                    # print("HTTP Status 500  服务器内部错误")
                else:
                    if 'completed' in r_dict:
                        if r_dict['completed'] == 'true':
                            return True
                        else:
                            self.show_time()
                            self.signal.emit("{} 视频播放进度{}%，《{}》课程学习进度{}%\n".format(video_name,
                                r_dict['completeRate'], course_name, r_dict['courseProgress']))
                            # print("视频播放进度{}%，课程学习进度{}%".format(r_dict['completeRate'], r_dict['courseProgress']))
                            return False
                    else:
                        return False
            else:
                return False

    def clear_list(self):
        video_id_list.clear()
        video_name_list.clear()
        completed_list.clear()
        course_info_list.clear()

    def print_list(self):
        print(video_id_list)
        print(video_name_list)
        print(completed_list)
        print(course_info_list)

    def run(self):
        global course_name, ONESCREEN
        for i, course_url in enumerate(course_url_list):
            self.show_time()
            self.signal.emit("开始学习第{}门课\n".format(i+1))
            driver.get(course_url)
            course_id = course_id_list[i]
            # print(course_id)
            try:
                # ele存在说明是双分屏或者三分屏
                # ele = driver.find_element_by_id('vodtree')
                ele = WebDriverWait(driver, 5, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'vodtree')))
            except:
                ONESCREEN = 1
            else:
                ONESCREEN = 0
            div = WebDriverWait(driver, 5, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'barleft')))
            if ONESCREEN == 1:
                course_name = div.text.strip("网络设置")
            else:
                course_name = div.text
            self.get_cookie()
            self.load_course(course_id)
            self.get_completed_video_list(course_id)
            if self.course_finished(course_id):
                self.show_time()
                self.signal.emit("《{}》课程全部视频学习完毕\n".format(course_name))
                # print("《{}》课程全部视频学习完毕".format(course_name))
                self.clear_list()
                continue
            else:
                for j, video_id in enumerate(video_id_list):
                    video_name = video_name_list[j]
                    self.show_time()
                    self.signal.emit("开始学习 {} 视频\n".format(video_name))
                    # print("开始学习 {} 视频".format(video_name))
                    self.select_video(course_id, video_id)
                    while True:
                        if self.video_finished(course_id, video_id, video_name):
                            self.show_time()
                            self.signal.emit("{} 视频学习完毕\n".format(video_name))
                            # print("{} 视频学习完毕".format(video_name))
                            break
                        else:
                            post(update_time_api, headers=header, cookies=cookie,
                                 data={'elsSign': cookie['eln_session_id']}, timeout=(15, 15))
                            sleep(180)
                    self.get_completed_video_list(course_id)
                    if self.course_finished(course_id):
                        self.show_time()
                        self.signal.emit("《{}》课程全部视频学习完毕\n".format(course_name))
                        # print("《{}》课程全部视频学习完毕".format(course_name))
                        self.clear_list()
                    sleep(1)
                self.clear_list()
            sleep(1)
            ONESCREEN = -1
        course_id_list.clear()
        course_url_list.clear()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 750)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(20)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(20)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(20)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 788, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton.clicked.connect(self.open_broswer)
        self.pushButton_2.clicked.connect(self.select_course)
        self.pushButton_3.clicked.connect(self.study_course)
        self.cursor = self.textBrowser.textCursor()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "一键学习"))
        self.pushButton.setText(_translate("MainWindow", "开始学习"))
        self.pushButton_2.setText(_translate("MainWindow", "选这门课"))
        self.pushButton_3.setText(_translate("MainWindow", "选课结束\n一键学习"))

    def open_broswer(self):
        self.thread = OpenBroswerThread()
        self.thread.signal.connect(self.set_text_broswer)
        self.thread.start()

    def set_text_broswer(self, text):
        # self.textBrowser.setText(text)
        self.textBrowser.append(text)
        self.textBrowser.moveCursor(self.cursor.End)

    def select_course(self):
        self.thread2 = SelectCourseThread()
        self.thread2.signal.connect(self.set_text_broswer)
        self.thread2.start()

    def study_course(self):
        self.thread3 = StudyCousre()
        self.thread3.signal.connect(self.set_text_broswer)
        self.thread3.start()


if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)
    app.setWindowIcon(QIcon(r"Images/foton.jpg"))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    exit(app.exec_())
