![GitHub last commit](https://img.shields.io/github/last-commit/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform)
![GitHub top language](https://img.shields.io/github/languages/top/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform)
![GitHub repo size](https://img.shields.io/github/repo-size/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform)
# 一键学习Bot
* 本程序仅供交流学习，强烈不建议使用本程序，强烈建议好好学习。<br>
* 如果你喜欢本程序，不妨点个star支持一下。<br>
## 小白使用说明<br>
* 下载[刷课程序](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/releases/download/0.99/StudyBotGUI.exe)
* 安装[Firefox浏览器](https://cdn.stubdownloader.services.mozilla.com/builds/firefox-stub/zh-CN/win/0244b03ff75452eec43ebfcabbe3fa2feda8105e3c426bd77b3d801cf01c05c7/Firefox%20Installer.exe)
* 下载geckodriver驱动程序，64位Windows操作系统请[点此](https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-win64.zip)下载
* 下载[使用说明](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/blob/master/%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.pdf)
## 进阶使用说明<br>
### 1.  环境配置：<br>
* Python3.7（安装selenium和requests库）<br>
* geckodriver.exe添加到环境变量<br>
* Firefox浏览器 版本 ≥ 60<br>
### 2. 功能说明：<br>
##### 自定义选课学习：
* **StudyBotGUI.exe**&emsp;图形界面学习,exe须和geckodriver位于同级目录，一次可循环添加多门课程<br>
* **RobotLearner.py**&emsp;一键秒学+挂机自动学习<br>
* **OneClickAfterTest.py**&emsp;手动选课，一键考试<br>
##### 根据学分批量选课学习：
* **GetAllCourseData.py**&emsp;获取当前福田大学中所有课程信息，保存在当前目录下的course_data.txt<br>
* **ChooseCourseByCredit.py**&emsp;&emsp;获取当前福田大学中所有我已经选课的课程信息，保存在当前目录下的course_progress.txt<br>
* 以下功能均需在获取课程信息的基础上进行
* **ChooseCourseByCredit.py**&emsp;按照学分批量选课<br>
* **StudyByCredit.py**&emsp;一键学习指定学分的所有课程（支持课前测试）<br>
* **ServerStudyBot.py**&emsp;云端Linux服务器一键学习（支持课前测试）<br>
* **ServerStudyBotTG.py**&emsp;云端Linux服务器一键学习（支持课前测试，支持推送学习进度到TelegramBot）<br>
* **CourseEvaluationBySelenium.py**&emsp;一键评价指定学分所有课程<br>
* **AfterTest.py**&emsp;一键考试指定学分的所有课程<br>
* **study.py**&emsp;study.ui生成的UI代码<br>
### 示例图片
![一键学习](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/blob/master/Images/%E4%B8%80%E9%94%AE%E5%AD%A6%E4%B9%A0.JPG)<br>
![一键选课](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/blob/master/Images/%E4%B8%80%E9%94%AE%E9%80%89%E8%AF%BE.JPG)<br>
![挂机学习](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/blob/master/Images/%E6%8C%82%E6%9C%BA%E5%AD%A6%E4%B9%A0.JPG)<br>
![云端学习进度推送](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/blob/master/Images/%E4%BA%91%E7%AB%AF%E5%AD%A6%E4%B9%A0%E6%8E%A8%E9%80%81.jpg)<br>
![云端学习进度推送到TG](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/blob/master/Images/%E6%8E%A8%E9%80%81TG.jpg)<br>
![图形界面exe程序](https://github.com/Idealisten/OneClickToLearnFotonUniversityOnlineStudyPlatform/blob/master/Images/GUI.jpg)<br>
