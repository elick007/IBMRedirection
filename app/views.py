from __future__ import unicode_literals

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
        fileHandler = FileHandler(url)
        fileHandler.start()
    return JsonResponse(data={"code": 0})


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
        hour = request.POST.get("hour")
        minute = request.POST.get("minute")

        def fun():
            os.system(f'python {fPath}')

        if scheduler.add_job(fun, 'cron', hour=hour, minute=minute, name=os.path.splitext(pFile.name)[0]):
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
                return JsonResponse(data={'data': 0, 'msg': 'success'})
        return JsonResponse(data={'data': -1, 'msg': 'task not exist'})
    else:
        return JsonResponse(data={'data': -1, 'msg': 'param name require'})


def sign_scheduler():
    commander = Commander()
    commander.login(("--auto",))
    commander.sign(['-a'])

fetch.get_all()
scheduler = BackgroundScheduler()
scheduler.add_job(sign_scheduler, 'cron', hour='10', minute='30', name='sign')
scheduler.add_job(fetch.get_all,'cron',day='13',hour='15', minute='50', name='91')
scheduler.start()
