from django.urls import path

from user.views import user_login, user_register, user_send_code, user_draw, find_pwd, modify_pwd, user_logout,test_baidu

app_name = 'user'

urlpatterns = [
    path('login', user_login, name='login'),
    path('register', user_register, name='register'),
    path('send_code', user_send_code, name='send_code'),
    path('draw', user_draw, name='draw'),
    path('find_pwd', find_pwd, name='find_pwd'),
    path('modify_pwd', modify_pwd, name='modify_pwd'),
    path('logout', user_logout, name='logout'),
    path('test_report', test_baidu, name='test_baidu'),
]
