from __future__ import unicode_literals

import _thread
import hashlib
import os
import time
from threading import Thread
from urllib.parse import unquote

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import render

from app.static.script import fetch
from cloud189.cli.cli import Commander
from django.views.decorators.csrf import csrf_exempt

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(CUR_DIR, 'static')


def index(request):
    return render(request, 'index.html')


def health(request):
    state = {"status": "UP"}
    return JsonResponse(state)


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


class FileHandler(Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def getfilename(self, headers):
        filename = ''
        if 'Content-Disposition' in headers and headers['Content-Disposition']:
            disposition_split = headers['Content-Disposition'].split(';')
            if len(disposition_split) > 1:
                if disposition_split[1].strip().lower().startswith('filename='):
                    file_name = disposition_split[1].split('=')
                    if len(file_name) > 1:
                        filename = unquote(file_name[1])
        if not filename and os.path.basename(self.url):
            filename = os.path.basename(self.url).split("?")[0]
        if not filename:
            return time.time()
        return filename

    def run(self) -> None:
        r = requests.get(url=self.url, allow_redirects=True, stream=True)
        file_name = self.getfilename(r.headers)
        file_path = os.path.join(STATIC_DIR, str(file_name))
        file_size = int(r.headers['Content-Length'])
        if file_size > 700 << 20:
            _md5 = hashlib.md5()
            for chunk in r.iter_content(chunk_size=4 << 20):
                if chunk:
                    _md5.update(chunk)
            hash_md5 = _md5.hexdigest().upper()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)
        commander = Commander()
        commander.login(("--auto",))
        commander.run_one('upload', [file_path])
        if os.path.exists(file_path): os.remove(file_path)


def download_file(request):
    url = request.GET.get('url')
    if url is not None:
        def task():
            commander = Commander()
            commander.login(("--auto",))
            commander.run_one('upload', ['--url', url])

        _thread.start_new_thread(task, ())
        return JsonResponse(data={"code": 0})
    else:
        return JsonResponse(data={"code": -1, "msg": "url require"})


@csrf_exempt
def add_cron_scheduler(request):
    if request.method == "POST":

        if pFile := request.FILES.get('file', None):
            fPath = os.path.join(STATIC_DIR, "script", pFile.name)
            with open(fPath, 'wb') as f:
                for chunk in pFile.chunks():
                    f.write(chunk)
        else:
            return JsonResponse(data={'code': -1, 'msg': 'upload file is empty'})
        day = request.POST.get("day")
        hour = request.POST.get("hour")
        minute = request.POST.get("minute")

        def fun():
            os.system(f'python {fPath}')

        if scheduler.add_job(fun, 'cron', day=day, hour=hour, minute=minute, name=os.path.splitext(pFile.name)[0]):
            return JsonResponse(data={"code": 0})
        else:
            return JsonResponse(data={"code": -1, 'msg': 'add job failed'})


def get_all_scheduler(request):
    return JsonResponse(data={'code': 0, 'msg': 'success', 'data': {'task': [s.name for s in scheduler.get_jobs()]}})


def del_scheduler(request):
    if name := request.GET.get("name"):
        for s in scheduler.get_jobs():
            if s.name == name:
                s.remove()
                pPath = os.path.join(STATIC_DIR, 'script', f'{name}.py')
                if os.path.exists(pPath): os.remove(pPath)
                return JsonResponse(data={'code': 0, 'msg': 'success'})
        return JsonResponse(data={'code': -1, 'msg': 'task not exist'})
    else:
        return JsonResponse(data={'code': -1, 'msg': 'param name require'})


def start_collect(request):
    category = request.GET.get('category')
    s_page = int(request.GET.get('startPage'))
    e_page = int(request.GET.get('endPage'))
    if category and s_page and e_page:
        fetch.get_all(category, s_page, e_page)
        return JsonResponse(data={'code': 0, 'msg': 'start to collect'})
    else:
        return JsonResponse(data={'code': -1, 'msg': 'params error'})


def sign_scheduler():
    commander = Commander()
    commander.login(("--auto",))
    commander.sign(['-a'])


@csrf_exempt
def download_xfile(request):
    if request.method == "POST":
        md5 = request.POST.get("md5")
        size = int(request.POST.get("size"))
        name = request.POST.get("name")
        url = request.POST.get("url")
        session_key = request.POST.get("sessionKey")
        session_secret = request.POST.get("sessionSecret")
        access_token = request.POST.get("accessToken")
        if md5 is None or size is None or name is None or url is None or session_key is None or session_secret is None or access_token is None:
            return JsonResponse(data={'code': -1, 'msg': 'params error'})
        client = Commander()
        client.upload_by_MD5info(md5, size, name, url, session_key, session_secret, access_token)
        return JsonResponse(data={'code': 0, 'msg': 'success'})


scheduler = BackgroundScheduler()
# scheduler.add_job(sign_scheduler, 'cron', day=None, hour='17', minute='09', name='sign')
# scheduler.add_job(fetch.get_all, 'cron', args=('tf', 1, 8), day='24', hour='19', minute='06', name='91')
# scheduler.start()
