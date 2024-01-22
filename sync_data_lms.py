import requests
import json
import re
f = open('data.json')
data = json.load(f)
f.close()
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
sync_data_course(data)
with open('data.json', 'w') as outfile:
    json.dump(data, outfile,ensure_ascii=False)
