import hashlib
import logging
import os
import random
import time
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.views import login
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Qinxiangshuge import settings
from Qinxiangshuge.settings import PONT_PATH
from user.models import User

import uuid

logger = logging.getLogger('log')


# 用户登录
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        password = request.POST.get('password')
        code = request.POST.get('code')
        code1 = request.session['code']
        rem_name = request.POST.get('rem_name')
        user = User.objects.filter(username=username).first()
        # 校验验证码是否正确
        if code.lower() == code1.lower():
            # 校验用户是否存在
            if user:
                # 校验用户是否是激活状态
                if user.is_active:
                    # 校验用户密码是否正确
                    if check_password(password, user.password):
                        response = redirect(reverse('novels:index'))
                        request.session['username'] = user.username
                        # 登录成功后，从客户端的cookie中取出key，并与user.uid绑定，存入cache中
                        liulanqi_key = request.COOKIES['liulanqi_key']
                        cache.set('liulanqi:' + user.uid, liulanqi_key)
                        if rem_name == 'on':
                            # 登录成功后，在cookie中设置值
                            response.set_cookie('uname', username)
                        return response
                    else:
                        return render(request, 'user/login.html', {'msg': '用户名和密码不正确'})
                else:
                    return render(request, 'user/login.html', {'msg': '用户名还未激活'})
            else:
                return render(request, 'user/login.html', {'msg': '用户名不存在'})
        else:
            return render(request, 'user/login.html', {'msg': '验证码有误'})
    else:
        username = request.COOKIES.get('uname', '')
        response = render(request, 'user/login.html', {'user': username})
        # 在登录GET请求时，从服务器端随机生成码，然后设置到浏览器的cookie中
        liulanqi_uuid = str(uuid.uuid1().hex)
        response.set_cookie('liulanqi_key', liulanqi_uuid)
        return response


# 用户注册
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        password = make_password(password)
        code = request.POST.get('code')
        is_author = request.POST.get('is_author')
        # 验证用户是否已注册
        user = User.objects.filter(username=username).first()
        if user:
            return render(request, 'user/register.html', {'msg': '用户名已被占用'})
        else:
            # 校验验证码是否正确
            # if code == request.session.get(phone):
            uid = str(uuid.uuid4().hex)
            user = User.objects.create(uid=uid, username=username, password=password, email=email, phone_num=phone)
            user.is_active = 1
            user.save()
            if is_author == 'on':
                user.is_author=1
                user.save()
            return redirect(reverse('user:login'))
            # else:
            #     return render(request, 'user/register.html', {'msg': '验证码有误'})
    else:
        visible = True
        return render(request, 'user/register.html',{'visible':visible})


# 获取验证码
def user_send_code(request):
    phone = request.GET.get('phone')
    # 寻求第三方服务：网易云信
    url = 'https://api.netease.im/sms/sendcode.action'
    headers = {}
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    headers['AppKey'] = 'c319e6d69853d2834d970fdd0d9b84b9'
    AppSecret = '03d4b504974c'
    Nonce = str(uuid.uuid4().hex)
    headers['Nonce'] = Nonce
    CurTime = str(int(time.time()))
    headers['CurTime'] = CurTime
    CheckSum = hashlib.sha1((AppSecret + Nonce + CurTime).encode('utf-8')).hexdigest()
    headers['CheckSum'] = CheckSum
    response = requests.post(url=url, data={'mobile': phone}, headers=headers)
    json_result = response.json()
    print(json_result)
    if json_result.get('code') == 200:
        request.session[phone] = json_result.get('obj')
        return JsonResponse({'msg': '短信发送成功！'})
    else:
        return JsonResponse({'msg': '短信发送失败！'})


# 登录验证码
def get_color():
    red = random.randint(0, 256)
    green = random.randint(0, 256)
    blue = random.randint(0, 256)
    return (red, green, blue)


def get_code():
    s = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    code = ''
    for i in range(4):
        code += random.choice(s)
    return code


def user_draw(request):
    width = 120
    height = 34
    image_size = (width, height)
    image = Image.new('RGB', image_size, get_color())
    draw = ImageDraw.Draw(image)
    for i in range(10):
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line((begin, end), fill=get_color())

    for i in range(20):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=get_color())

    code = get_code()
    myfont = ImageFont.truetype(font=os.path.join(PONT_PATH, 'verdana.ttf'), size=30)
    for i in range(4):
        distance_x = random.randint(30 * i, 30 * i + 5)
        distance_y = random.randint(0, 5)
        draw.text((distance_x, distance_y), code[i], font=myfont, fill=get_color())
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    buffer = BytesIO()
    image.save(buffer, 'jpeg')
    buf_bytes = buffer.getbuffer()
    request.session['code'] = code
    return HttpResponse(buf_bytes, 'image/jpeg')


# 找回密码
def find_pwd(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        email = request.POST.get('email')
        user = User.objects.filter(username=username, email=email).first()
        logger.info('该用户需要进行找回密码{}'.format(user.uid))
        if user:
            # 生成token
            token = str(uuid.uuid4().hex)
            request.session[token] = user.uid
            logger.info('token的绑定情况为{}--->{}'.format(token, user.uid))
            path = 'http://127.0.0.1:8000/user/modify_pwd?token={}'.format(token)  # 信息格式化

            # 发送邮箱
            subject = '琴香书阁找回密码邮件'
            message = '''
                欢迎注册琴香书阁会员！亲爱的用户请赶快找回密码使用吧！
                <a href='{}'>点击重置密码</a>   
                如果链接不可用可以复制以下内容到浏览器激活：{}
    
                                                琴香书阁开发团队   
                '''.format(path, path)
            result = send_mail(subject=subject, message='', from_email=settings.EMAIL_HOST_USER,
                               recipient_list=[email, ],
                               html_message=message)
            if result == 1:
                return HttpResponse('邮箱发送成功')
            else:
                return HttpResponse('邮箱发送失败')
        else:
            return render(request, 'user/find_pwd.html', {'msg': '用户名或邮箱有误'})
    return render(request, 'user/find_pwd.html')


# 修改密码
def modify_pwd(request):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        token = request.GET.get('token')

        # 获取session中值
        uid = request.session.get(token)
        logger.info('通过token：{}获取到的用户uid：{}'.format(token, uid))
        password = make_password(new_password)
        User.objects.filter(uid=uid).update(password=password)
        return HttpResponse('密码修改成功')
    else:
        token = request.GET.get('token')
        return render(request, 'user/modify_pwd.html', locals())


# 注销
def user_logout(request):
    logout(request)
    return redirect(reverse("user:login"))


def test_baidu(request):
    return render(request,'user/test.html')
