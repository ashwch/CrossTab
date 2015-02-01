from django.conf.urls import patterns, url

from app.views import ClassicLogin, ClassicSignUP, Cross_tabulate, File_upload, Home, Load_old_file,\
    Login, Logout


urlpatterns = patterns('',
                       url(r'^$', Home.as_view(), name='home'),
                       url(r'^login/$', Login.as_view(), name='login'),
                       url(r'^classiclogin/$', ClassicLogin.as_view(), name='classiclogin'),
                       url(r'^logout/$', Logout.as_view(), name='logout'),
                       url(r'^home/$', Home.as_view(), name='home'),
                       url(r'^signup', ClassicSignUP.as_view(), name='signup'),
                       url(r'^upload', File_upload.as_view(), name='file_upload'),
                       url(r'^cross_tabulate', Cross_tabulate.as_view(), name='cross_tabulate'),
                       url(r'^load_old_file', Load_old_file.as_view(), name='load_old_file'),
                       )
