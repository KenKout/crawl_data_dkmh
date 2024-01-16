import requests
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
import html2text
import re
import time
import json
start_time = time.time()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
def login_sso():
    url = "https://sso.hcmut.edu.vn/cas/login?service=https://mybk.hcmut.edu.vn/my/homeSSO.action"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    resp = s.get(url, headers=headers).text
    lt = resp.split('<input type="hidden" name="lt" value="')[1].split('" />')[0]
    execution = resp.split('<input type="hidden" name="execution" value="')[1].split('" />')[0]
    data = f"username={username}&password={password}&execution={execution}&_eventId=submit&submit=Login&lt={lt}"
    resp2 = s.post(url, headers=headers, data=data)
    print('Function - Login: Success')

def get_info_monhocID(hocKyId,dotDKId):

    resp1 = s.get('https://mybk.hcmut.edu.vn/dkmh', headers=headers)
    resp2 = s.get('https://mybk.hcmut.edu.vn/dkmh/home.action', headers=headers)
    resp3 = s.get('https://mybk.hcmut.edu.vn/dkmh/dangKyMonHocForm.action', headers=headers)
    # Select Dot DKMH
    resp4 = s.post('https://mybk.hcmut.edu.vn/dkmh/ketQuaDangKyView.action', headers=headers, data=f"hocKyId={hocKyId}")
    resp5 = s.post('https://mybk.hcmut.edu.vn/dkmh/getDanhSachDotDK.action', headers=headers, data=f"hocKyId={hocKyId}")
    resp6 = s.post('https://mybk.hcmut.edu.vn/dkmh/getLichDangKy.action', headers=headers, data=f"dotDKId={dotDKId}&dotDKHocVienId={dotDKId}")
    resp7 = s.post('https://mybk.hcmut.edu.vn/dkmh/getDanhSachMonHocDangKy.action', headers=headers, data=f"dotDKId={dotDKId}")
    resp8 = s.post('https://mybk.hcmut.edu.vn/dkmh/getKetQuaDangKy.action', headers=headers)
    resp9 = s.post('https://mybk.hcmut.edu.vn/dkmh/searchMonHocDangKy.action', headers=headers, data=f"msmh= ")
    monHocId = []
    for line in resp9.text.split('\n'):
        if "<tr  id='monHoc" in line:
            monHocId.append(line.split("<tr  id='monHoc")[1].split("'")[0])
    print(monHocId)
    return monHocId

def convert_html_to_text(html_content):

    # Initialize the HTML to Text converter
    html_to_text = html2text.HTML2Text()

    # Set options for the converter
    html_to_text.body_width = 0  # No line wrapping
    html_to_text.ignore_links = True  # Ignore hyperlinks
    html_to_text.ignore_images = True  # Ignore images

    # Convert HTML to plain text
    plain_text = html_to_text.handle(html_content)
    return plain_text


def parse_schedule_text(text, id):
    lines = text.split("\n")
    current_class = {}
    new_teacher = {}
    # Regular expressions for the various parts we are interested in
    subject_pattern = re.compile(r".+([A-Z]{2}\d{4})\s-\s(.+)")
    time_and_location_pattern = re.compile(
        r"(Thứ [0-9]|Chủ\snhật).+\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)"
    )
    teacher_info = re.compile(
        r"([A-Z0-9_]{3,9})\s\s\|(.{0,10})\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|"
    )
    week_pattern_regex = re.compile(r"(\d[-\d]*)")

    # Mapping of Vietnamese days to day of the week
    day_mapping = {
        "Thứ 2": 1,
        "Thứ 3": 2,
        "Thứ 4": 3,
        "Thứ 5": 4,
        "Thứ 6": 5,
        "Thứ 7": 6,
        "Chủ nhật": 0,
    }

    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        subject_match = subject_pattern.match(line)
        if subject_match:
            # When a new subject is found, create new json object
            current_class = {
                "id": id,
                "maMonHoc": subject_match.group(1),
                "tenMonHoc": subject_match.group(2).strip(),
                "soTinChi": 0,
                "lichHoc": [],
            }
            continue
        teacher_info_match = teacher_info.match(line)
        if teacher_info_match:
            if current_class != {} and new_teacher != {}:
                try:
                    current_class["lichHoc"].append(new_teacher)
                except:
                    pass
            else:
                pass
            new_teacher = {
                "group": teacher_info_match.group(1),
                "siso": teacher_info_match.group(2).strip(),
                "ngonNgu": teacher_info_match.group(3).strip(),
                "nhomLT": teacher_info_match.group(4).strip(),
                "giangVien": teacher_info_match.group(5).strip(),
                "nhomBT": teacher_info_match.group(6).strip(),
                "giangVienBT": teacher_info_match.group(7).strip(),
                "sisoLT": teacher_info_match.group(8).strip(),
                "classInfo": [],
            }
        time_and_location_match = time_and_location_pattern.findall(line)
        if time_and_location_match:
            for match in time_and_location_match:
                day, time, location, coso, temp, week = list(match)
                digits = week.strip().replace("\\", "")
                classInfo = {
                    "dayOfWeek": day_mapping[day],
                    "tietHoc": [eval(i) for i in re.findall(r"[0-9]{1,2}", time)],
                    "phong": location.strip(),
                    "coSo": coso,
                    "week": [int(digit) + 10 * (i // 10) if digit != '0' else 10 * (i // 9) for i, digit in
                             enumerate(digits) if digit.isdigit()]

                }
                new_teacher["classInfo"].append(classInfo.copy())
            continue
        ''' Uncomment this block to see how the week pattern is parsed
        input_string = "1234--789-1234----9012----7---"
        #digits = [int(x) for x in input_string if x.isdigit()]
        digits = [x for x in input_string]

        result = []
        for i, digit in enumerate(digits):
            try:
                # Try to convert the current character to an integer
                digit = int(digit)
                if digit == 0:
                    # If the digit is '0', it represents a multiple of 10 (10, 20, 30, etc.)
                    # The multiple is determined by the current index divided by 9
                    result.append(10 * ((i // 9)))
                else:
                    # For non-zero digits, add 9 for each complete set of 10 digits processed
                    result.append(digit + 10 * (i // 10))
            except:
                pass
        '''
    try:
        current_class["lichHoc"].append(new_teacher)
    except:
        pass
    print(current_class)
    return current_class



s = requests.Session()
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/x-www-form-urlencoded"
login_sso()
monHocId = get_info_monhocID('563','645')
final_result = []
for id in monHocId:
    info = s.post('https://mybk.hcmut.edu.vn/dkmh/getThongTinNhomLopMonHoc.action', headers=headers, data=f"monHocId={id}")
    data = convert_html_to_text(info.text)
    result = parse_schedule_text(data, id)
    if result != {}:
        final_result.append(result)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)
end_time = time.time()
print(end_time - start_time)
