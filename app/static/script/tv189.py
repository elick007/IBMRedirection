import json
import requests
import random

users = {'unames': ['BDXlIFCyDITB2FwqIG8rTw==',  # 189
                    '4JbMc+sqn0cH+Cl5JgcTEw==',  # 134
                    'xTaSwzbCbuXYERpm9WKUBQ==',  # 158
                    ], 'upass': 'LUXWSieEVbZ8F+VZeTzLxg=='}
if __name__ == '__main__':
    _session = requests.session()
    resp = _session.get('http://h5.nty.tv189.com/csite/tysx/uc/login-by-pass?goBackUrl=')
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://h5.nty.tv189.com",
        "Referer": "http://h5.nty.tv189.com/csite/tysx/uc/login-by-pass?goBackUrl=",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36/newtysx-android-ua-5.5.9.39",
        "X-Requested-With": "XMLHttpRequest"}
    for user in users['unames']:
        login_resp = _session.post('http://h5.nty.tv189.com/api/portal/h5inter/login',
                                   data={'uname': user, 'upass': users['upass']},
                                   headers=headers)
        login_json = json.loads(login_resp.text)
        if login_json.get('code') == 0:
            # signed
            headers['Referer'] = "http://h5.nty.tv189.com/csite/tysx/task/index"
            print("sign: " + _session.get("http://h5.nty.tv189.com/api/portal/task/integralpresentforsign",
                                          headers=headers).text)
            print(
                "share: " + _session.get(
                    f"http://h5.nty.tv189.com/api/portal/task/shareintegralapply?{random.random()}",
                    headers=headers).text)
            print("festival: " + _session.get(f"http://h5.nty.tv189.com/api/portal/task/festival-get?{random.random()}",
                                         headers=headers).text)
            headers['Referer'] = 'http://h5.nty.tv189.com/csite/tysx/task/normalscreen'
            tasks = ['1', '5', '30']
            for task in tasks:
                task_resp = _session.get(f"http://h5.nty.tv189.com/api/portal/task/playtask?e={task}", headers=headers)
                print(task_resp.text)
        else:
            print(f"login failed {user}")
