from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    '''
    id
    username,password,last_login,is_superuser,first_name,last_name,email,is_staff,is_active,date_joined

    添加字段：
    phone_num,head_img,last_ip,uuid
    '''

    phone_num = models.CharField(max_length=11, unique=True, null=False, verbose_name='手机号码')
    head_img = models.ImageField(upload_to='uploads/%Y/%m/', verbose_name='用户头像')
    last_ip = models.CharField(max_length=32, verbose_name='最后登录IP')
    uid = models.CharField(primary_key=True, max_length=40, unique=True, null=False)
    is_author = models.SmallIntegerField(default=0, choices=((0, '普通用户'), (1, '作者')), verbose_name='是否是作者')

    class Meta:
        db_table = 'user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
