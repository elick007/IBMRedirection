from __future__ import unicode_literals

import os
from threading import Thread

import requests
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import render
from cloud189.cli.cli import Commander

CUR_DIR = os.path.abspath(os.path.dirname(__file__))


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

    def run(self) -> None:
        r = requests.get(url=self.url, allow_redirects=True)
        file_name = str.__hash__(self.url)
        file_path = os.path.join(CUR_DIR, 'static', str(file_name))
        with open(file_path, 'wb') as f:
            f.write(r.content)
        commander = Commander()
        commander.login(("--auto",))
        commander.run_one('upload',[file_path])


def download_file(request):
    url = request.GET.get('url')
    if url is not None:
        fileHandler = FileHandler(url)
        fileHandler.start()
    return JsonResponse(data={"code": 0})
