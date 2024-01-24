import requests
import json
import re
from requests.structures import CaseInsensitiveDict
import html2text
import unidecode
from unidecode import unidecode

f = open('data.json')
data = json.load(f)
f.close()

f = open('data_lecturer.json')
data_lecturer = json.load(f)
f.close()

s = requests.Session()
def sync_data_course(data):
    for i in data:
        for j in i['lichHoc']:
            if j['giangVien'] == '' or j['giangVien'] == '_"Chưa/Đang phân công"_'  or j['giangVien'] == 'Chờ Phân Công CBGD':
                print(j)
                try:group = j['group'].split('_')[0]
                except:group = j['group']
                while True:
                    try:
                        get_data = requests.get(f'https://lms.hcmut.edu.vn/course/search.php?areaids=core_course-course&q=232+{i["maMonHoc"]}+{group}', timeout=5)
                        break
                    except:
                        pass
                regex = re.compile(r'Teacher: </span><a href="https://lms.hcmut.edu.vn/user/profile.php\?id=(\d+)">(.+)</a></li></ul>')
                match = regex.search(get_data.text)
                if match:
                    print(match.group(2))
                    j['giangVien'] = match.group(2)
            if (j['giangVienBT'] == '' or j['giangVienBT'] == '_"Chưa/Đang phân công"_' or j['giangVienBT'] == 'Chờ Phân Công CBGD') and '_' in j['group'] :
                print(j)
                try:group = j['group'].split('_')[1]
                except:group = j['group']
                regex = re.compile(r'[0-9]{4}')
                number = regex.search(i["maMonHoc"])
                monhoc = i["maMonHoc"].replace(number.group(),(str(int(number.group())+1)))
                while True:
                    try:
                        get_data = requests.get(f'https://lms.hcmut.edu.vn/course/search.php?areaids=core_course-course&q=232+{monhoc}+{group}', timeout=5)
                        break
                    except:
                        pass
                regex = re.compile(r'Teacher: </span><a href="https://lms.hcmut.edu.vn/user/profile.php\?id=(\d+)">(.+)</a></li></ul>')
                match = regex.search(get_data.text)
                if match:
                    print(match.group(2))
                    j['giangVienBT'] = match.group(2)

def login_sso(user,password,s):
    url = "https://sso.hcmut.edu.vn/cas/login?service=https://mybk.hcmut.edu.vn/my/homeSSO.action"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    resp = s.get(url, headers=headers).text
    lt = resp.split('<input type="hidden" name="lt" value="')[1].split('" />')[0]
    execution = resp.split('<input type="hidden" name="execution" value="')[1].split('" />')[0]
    data = f"username={user}&password={password}&execution={execution}&_eventId=submit&submit=Login&lt={lt}"
    resp2 = s.post(url, headers=headers, data=data)
    print('Function - Login: Success')

def get_lecturer_link(s):
    login = s.get('https://lms.hcmut.edu.vn/login/index.php?authCAS=CAS',timeout=5).text
    data = s.get('https://lms.hcmut.edu.vn/course/search.php?search=232&perpage=all').text
    regex = re.compile(r'https\://lms\.hcmut\.edu\.vn/user/profile.php\?id=[0-9]{1,10}')
    match = regex.findall(data)
    return match

def sync_data_lecturer(data,s):
    for i in data:
        is_exist = False
        resp = s.get(i).text
        decode_html = html2text.html2text(resp)
        #print(decode_html)
        regex_name = re.compile(r'\n#\s(.+)')
        regex_email = re.compile(r'Địa\schỉ\sthư\sđiện\stử\n.+\[(.+)\]')
        try:
            email = regex_email.findall(decode_html)[0]
        except:
            email = ''
        name = regex_name.findall(decode_html)[0]
        for j in data_lecturer:
            if unidecode(j['name']).lower() == unidecode(name).lower():
                j['email'] = email
                print('Update email for',name)
                is_exist = True
                break
        if is_exist == False:
            new_data = {'name':name,'email':email,'phone':''}
            data_lecturer.append(new_data)
            print('Add new lecturer',name)

sync_data_course(data)
with open('data.json', 'w') as outfile:
    json.dump(data, outfile,ensure_ascii=False)

login_sso(user,password,s)
match = list(dict.fromkeys(get_lecturer_link(s)))
sync_data_lecturer(match,s)

with open('data_lecturer.json', 'w') as outfile:
    json.dump(data_lecturer, outfile,ensure_ascii=False)
