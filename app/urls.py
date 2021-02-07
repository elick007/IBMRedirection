from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('health', views.health, name='health'),
    path('404', views.handler404, name='404'),
    path('500', views.handler500, name='500'),
    path('download', views.download_file, name='download'),
    path('addtask', views.add_cron_scheduler, name='addtask'),
    path('gettask', views.get_all_scheduler, name='gettask'),
    path('deltask', views.del_scheduler, name='deltask'),
    path('collect91', views.start_collect, name='collect'),
    path('upload', views.download_xfile, name='upload')
]
