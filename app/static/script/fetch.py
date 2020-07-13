import base64
import os
import random
import re
from concurrent.futures.thread import ThreadPoolExecutor

from bs4 import BeautifulSoup, Comment
import requests

from cloud189.cli.cli import Commander

STATIC_DIR = os.path.abspath(os.path.dirname(__file__))
mf_url = 'http://www.91porn.com/v.php?category=mf&viewtype=basic&page=4'
headers = {'Referer': 'http://www.91porn.com/index.php', 'Domain-Name': 'porn9_video_domain_name',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
           }
headers_1 = {
    'Referer': 'http://www.91porn.com/index.php', 'Domain-Name': 'porn9_video_domain_name',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'X-Forwarded-For': '104.206.141.12'
}
url_aria2 = 'http://104.206.144.11:6800/jsonrpc'

executor = ThreadPoolExecutor()


def get_mf_list(url):
    mf_html = requests.get(url, headers=headers_1)
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
    parse_url(dict([mf_list.popitem()]))


def fetch_html(url):
    html = requests.get(url=url, headers=headers_1).text
    if ((html.find('你每天只可观看25个视频') != -1) or (html.find('you can only watch 25 videos') != -1)):
        headers_1['X-Forwarded-For'] = str(random.randrange(0, 255)) + '.' + str(
            random.randrange(0, 255)) + '.' + str(random.randrange(0, 255)) + '.' + str(random.randrange(0, 255))
        fetch_html(url)
    else:
        return html.text


def parse_url(mf_dict):
    for key, value in mf_dict.items():
        html = fetch_html(value)
        match = re.search('document.write\(strencode\("(.+)","(.+)",.+\)\);', html)
        if match:
            param1 = match.group(1)
            param2 = match.group(2)
        else:
            print(f"don't match:{value}")
            continue
        param1 = str(base64.decodebytes(str.encode(param1)), 'utf-8')
        str_org = ''
        for i in range(0, len(param1)):
            k = i % len(param2)
            str_org += chr(ord(param1[i]) ^ ord(param2[k]))
        parser_out = str(base64.decodebytes(str.encode(str_org)), 'utf-8')
        real_url = BeautifulSoup(parser_out, 'html.parser').find('source')['src']
        upload(real_url, name=key)


def upload(url, name):
    r = requests.get(url=url, allow_redirects=True, stream=True)
    file_path = os.path.join(STATIC_DIR, f"{name}.mp4")
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: f.write(chunk)
    commander = Commander()
    commander.login(("--auto",))
    commander.run_one('upload', [file_path])
    if os.path.exists(file_path): os.remove(file_path)


def get_all():
    for i in range(1, 6):
        mf_url = 'http://www.91porn.com/v.php?category=mf&viewtype=basic&page={0}'.format(i)
        executor.submit(get_mf_list, (mf_url))


if __name__ == '__main__':
    # get_all()
    mf_url = 'http://www.91porn.com/v.php?category=mf&viewtype=basic&page={0}'.format(1)
    get_mf_list(mf_url)
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
