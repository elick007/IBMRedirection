import base64
import os
import random
import re
import time
from concurrent.futures.thread import ThreadPoolExecutor

from bs4 import BeautifulSoup, Comment
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from cloud189.cli.cli import Commander

STATIC_DIR = os.path.abspath(os.path.dirname(__file__))
mf_url = 'http://www.91porn.com/v.php?category=mf&viewtype=basic&page=4'
headers = {'Referer': 'http://www.91porn.com/index.php', 'Domain-Name': 'porn9_video_domain_name',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
           }
headers_1 = {
    'Referer': 'http://www.91porn.com/index.php', 'Domain-Name': 'porn9_video_domain_name',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'X-Forwarded-For': '104.216.141.12'
}
url_aria2 = 'http://104.206.144.11:6800/jsonrpc'

executor = ThreadPoolExecutor()
s = requests.Session()
retries = Retry(total=3, backoff_factor=1)
s.mount('http', HTTPAdapter(max_retries=retries))


def get_mf_list(url):
    mf_html = s.get(url, headers=headers_1)
    mf_list = {}
    soup = BeautifulSoup(mf_html.text, 'html.parser')
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()
    image_channel = soup.find_all('div', class_='well well-sm videos-text-align')
    for channel in image_channel:
        a = channel.find('a', recursive=False)
        detail_url = a.get('href')
        title = a.find('span', recursive=False).text
        mf_list.__setitem__(title, detail_url)
    return mf_list


def fetch_html(url, header):
    headers_1['X-Forwarded-For'] = str(random.randrange(0, 255)) + '.' + str(
        random.randrange(0, 255)) + '.' + str(random.randrange(0, 255)) + '.' + str(random.randrange(0, 255))
    resp = s.get(url=url, headers=headers_1)
    if resp is None or resp.status_code != 200 or resp.text.find('你每天只可观看25个视频') != -1:
        time.sleep(0.5)
        return fetch_html(url, headers_1)
    else:
        soup = BeautifulSoup(resp.text, 'html.parser')
        area = soup.find('textarea')
        if area is not None:
            video = area.text
        else:
            print(f"non share URL={url}")
            return None
        return fetch_share(video)


def fetch_share(url):
    resp = s.get(url, headers=headers)
    if resp.status_code != 200 or resp is None:
        time.sleep(0.5)
        return fetch_share(url)
    else:
        return resp.text


def parse_url(title, url):
    try:
        html = fetch_html(url, headers_1)
        match = re.search('document.write\\(strencode\\("(.+)","(.+)",.+\\)\\);', html)
        if match:
            param1 = match.group(2)
            param2 = match.group(1)
        else:
            print(f"not encryption:{url}")
            soup = BeautifulSoup(html, 'html.parser')
            video = soup.find('video').find('source').get('src')
            upload(video, title)
            return
        param1 = str(base64.decodebytes(str.encode(param1)), 'utf-8')
        str_org = ''
        for i in range(0, len(param1)):
            k = i % len(param2)
            str_org += chr(ord(param1[i]) ^ ord(param2[k]))
        parser_out = str(base64.decodebytes(str.encode(str_org)), 'utf-8')
        real_url = BeautifulSoup(parser_out, 'html.parser').find('source')['src']
    except Exception as e:
        print(e)
        return
    upload(real_url, name=title)


def upload(url, name):
    print("url=" + url)
    file_path = ''
    try:
        r = s.get(url=url, headers=headers_1, allow_redirects=True, stream=True)
        if r.status_code != 200:
            print(r)
            return
        file_path = os.path.join(STATIC_DIR, f"{name}.mp4")
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)
        # os.system(f"echo a>>{file_path}")
        commander = Commander()
        commander.login(("--auto",))
        commander.run_one('upload', [file_path])
    except Exception as e:
        print(e)
    finally:
        if os.path.exists(file_path): os.remove(file_path)


def get_all(category, s_page: int, e_page: int):
    all_dict = {}
    for i in range(s_page, e_page):
        mf_url = f'http://www.91porn.com/v.php?category={category}&viewtype=basic&page={i}'
        all_dict.update(get_mf_list(mf_url))
    for i, (k, v) in enumerate(all_dict.items()):
        executor.submit(parse_url, k, v)


if __name__ == '__main__':
    get_all('tf', 5, 7)
    # parse_url("jj",'http://91.9p9.xyz/ev.php?VID=bf54JLJFfztRZFFXLdE8zkkEbCqhPrm3sDulKFKSPFyKmc42')
    # parse_url("tete","http://www.91porn.com/view_video.php?viewkey=248dc390fd47f747d762&page=5&viewtype=basic&category=tf")
    # mf_url = 'http://www.91porn.com/v.php?category=mf&viewtype=basic&page={0}'.format(1)
    # get_mf_list(mf_url)
    # _thread.start_new_thread(get_mf_list, (mf_url,))
    # exit(0)
    # for i in range(17, 26, 2):
    #     mf_url = 'http://www.91porn.com/v.php?category=mf&viewtype=basic&page={0}'.format(i)
    #     mf_url_2 = 'http://www.91porn.com/v.php?category=mf&viewtype=basic&page={0}'.format(i + 1)
    #     try:
    #         _thread.start_new_thread(get_mf_list, (mf_url,))
    #         _thread.start_new_thread(get_mf_list, (mf_url_2,))
    #     except Exception as e:
    #         print('线程出错')
    #         raise e
    #     while 1:
    #         pass
    # get_mf_list(mf_url)
