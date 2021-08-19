from django.db import models

from user.models import User
from tinymce.models import HTMLField

class NovelsType(models.Model):
    '''小说类别表'''
    typename = models.CharField(max_length=30, verbose_name='小说类别名称')
    logo = models.CharField(max_length=30, verbose_name='类别标识')
    image = models.ImageField(upload_to='type', verbose_name='类别图片')
    status = models.SmallIntegerField(default=1, choices=((0, '禁用'), (1, '使用中')), verbose_name='类别状态')

    class Meta:
        db_table = 'novels_type'
        verbose_name = '小说类别表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.typename


class Novels(models.Model):
    '''小说表'''
    type = models.ForeignKey('NovelsType', verbose_name='小说类别', on_delete=models.CASCADE)
    uid = models.CharField(primary_key=True, max_length=40, unique=True, null=False)
    novel_name = models.CharField(max_length=20, verbose_name='小说书名')
    title = models.CharField(max_length=50, verbose_name='小说标题')
    desc = models.TextField(verbose_name='概述')
    author = models.CharField(max_length=20, verbose_name='作者')
    image = models.ImageField(upload_to='novels', verbose_name='小说图片')
    status = models.SmallIntegerField(default=1, choices=((0, '下线'), (1, '上线')), verbose_name='小说状态')
    is_delete = models.SmallIntegerField(default=0, choices=((0, '不删除'), (1, '删除')), verbose_name='是否删除')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,default='')

    class Meta:
        db_table = 'novels'
        verbose_name = '小说表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.novel_name


class ViceNovels(models.Model):
    '''小说副表'''
    novels = models.OneToOneField(to=Novels, on_delete=models.CASCADE)
    uid = models.CharField(primary_key=True, max_length=40, unique=True, null=False)
    hits = models.IntegerField(default=0, verbose_name='点击量')
    collection = models.IntegerField(default=0, verbose_name='收藏量')

    class Meta:
        db_table = 'novels_vice'
        verbose_name = '小说副表'
        verbose_name_plural = verbose_name


class Chapter(models.Model):
    '''小说章节表'''
    novels = models.ForeignKey(to=Novels, on_delete=models.CASCADE)
    uid = models.CharField(primary_key=True, max_length=40, unique=True, null=False)
    chaptername = models.CharField(max_length=20, verbose_name='章节名称')
    path = models.CharField(max_length=200, verbose_name='存储路径',default='')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # text=HTMLField(verbose_name='章节正文',default='')

    class Meta:
        db_table = 'novels_chapter'
        verbose_name = '小说章节表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.chaptername


class Collection(models.Model):
    '''小说收藏表'''
    novels = models.ForeignKey(to=Novels, on_delete=models.CASCADE)
    uid = models.CharField(primary_key=True, max_length=40, unique=True, null=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    Collec_time = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        db_table = 'novels_collection'
        verbose_name = '小说收藏表'
        verbose_name_plural = verbose_name


class Hits(models.Model):
    '''小说点赞表'''
    novels = models.ForeignKey(to=Novels, on_delete=models.CASCADE)
    uid = models.CharField(primary_key=True, max_length=40, unique=True, null=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    hits_time = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        db_table = 'novels_hits'
        verbose_name = '小说点赞表'
        verbose_name_plural = verbose_name

class IndexBanner(models.Model):
    '''首页中的推荐'''
    novels = models.ForeignKey(to=Novels, on_delete=models.CASCADE, verbose_name='小说书名')
    image = models.ImageField(upload_to='banner', verbose_name='小说推荐图片')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    class Meta:
        db_table = 'index_banner'
        verbose_name = '首页推荐图'
        verbose_name_plural = verbose_name

class MyBookrack(models.Model):
    '''我的书架'''
    user = models.ForeignKey(to=User,on_delete=models.CASCADE)
    novels = models.ForeignKey(to=Novels, on_delete=models.CASCADE)
    chapters_uid = models.IntegerField(verbose_name='章节id',null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间',null=False)
    is_delete = models.SmallIntegerField(default=0, choices=((0, '不删除'), (1, '删除')), verbose_name='是否删除')

    class Meta:
        db_table = 'mybookrack'
        verbose_name = '我的书架表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username
