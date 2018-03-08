#coding=utf-8
import re
import json
import requests
import sys

try:
    username = sys.argv[1]
    password = sys.argv[2]
except Exception as err:  
    print('请输入用户名 密码')
    exit()

loginUrl = 'https://sso.buaa.edu.cn/login?service=http%3A%2F%2F10.200.21.61%3A7001%2Fieas2.1%2Fwelcome'

session = requests.Session()
response = session.get(loginUrl)
content = response.text

ltPattern = re.compile('name="lt".*?value="(.*?)"')
lts =  re.findall(ltPattern, content)

executionPattern = re.compile('name="execution".*?value="(.*?)"')
executions = re.findall(executionPattern, content)

eventIdPattern = re.compile('name="_eventId".*?value="(.*?)"')
eventIds = re.findall(eventIdPattern, content)

postLoginUrl = 'https://sso.buaa.edu.cn/login'
params = {
    'lt': lts[0],
    'execution': executions[0],
    '_eventId': eventIds[0],
    'username': username,
    'password': password,
    'submit': '登录'
}

headers = {
    'Origin' : 'https://sso.buaa.edu.cn',
    'referer': 'https://sso.buaa.edu.cn',
    'DNT': '1'
}

postLoginResponse = session.post(postLoginUrl, data=params, headers=headers)

successPatterm = re.compile('<div id="setting">')
successTexts = re.findall(successPatterm, postLoginResponse.text)
if len(successTexts) > 0:
    print('登录成功')
else:
    successPatterm = re.compile('<p class="success_phone">')
    successTexts = re.findall(successPatterm, postLoginResponse.text)
    if len(successTexts) == 0:
        print('登录失败')
        exit()
    else:
        print('登录成功')

gradeUrl = 'http://10.200.21.61:7001/ieas2.1/cjcx/queryTyQmcj'
gradeResponse = session.get(gradeUrl)

termPatterm = re.compile('<option value="(.*?)" >\d{4}')
terms = re.findall(termPatterm, gradeResponse.text)

allCourses = []
for term in terms:
    params = { 'pageXnxq': term }
    response = session.post(gradeUrl, params)
    coursePatterm = re.compile(r'<tr.*?>.*?<td>(\d{1,2})</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', re.S)
    courses = re.findall(coursePatterm, response.text)
    allCourses = allCourses + courses

compulsoryCourse = []
compulsoryCredit = 0
publicElectiveCourse = []
publicElectiveCredit = 0
majorElectiveCourse = []
majorElectiveCredit = 0

for course in allCourses:
    if course[5] == '必修'.decode('utf-8'):
        compulsoryCourse.append(course)
    elif course[5] == '选修'.decode('utf-8') and course[6] == '专业课程'.decode('utf-8'):
        majorElectiveCourse.append(course)
    else:
        publicElectiveCourse.append(course)

print('\n必修课')
print('课程名 课程类别 学分 ')
for course in compulsoryCourse:
    print(course[4] + ' ' + course[6] + ' ' + course[7] + ' ' + course[1])
    compulsoryCredit += float(course[7])

print('\n公选课')
print('课程名 课程类别 学分 ')
for course in publicElectiveCourse:
    print(course[4] + ' ' + course[6] + ' ' + course[7] + ' ' + course[1])
    publicElectiveCredit += float(course[7])

print('\n专业选修课')
print('课程名 课程类别 学分 ')
for course in majorElectiveCourse:
    print(course[4] + ' ' + course[6] + ' ' + course[7] + ' ' + course[1])
    majorElectiveCredit += float(course[7])

print('\n\n必修课学分: ' + str(compulsoryCredit))
print('公选课学分: ' + str(publicElectiveCredit))
print('专业选修课学分： ' + str(majorElectiveCredit))
