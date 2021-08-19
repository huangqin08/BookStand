import uuid
from alembic import context
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse, NoReverseMatch
from novels.models import NovelsType, IndexBanner, Novels, Chapter, MyBookrack, Hits
from user.models import User
from django.core.cache import cache
import logging
from django.contrib.auth import logout

logger = logging.getLogger('log')


# 首页
def index(request):
    '''登录判断'''
    user = request.session.get('username')

    if user:
        user = User.objects.filter(username=user).first()
        # 在首页中，判断是否在另一个浏览器登录了，从cache中取出登陆时存入的key
        liulanqi_key = cache.get('liulanqi:' + user.uid)
        logger.info('缓存中的key为：{}----浏览器中的key为:{}'.format(liulanqi_key, request.COOKIES['liulanqi_key']))
        # 校验当前浏览器中cookie中取出的key是否与cache中取出的key不一致
        if request.COOKIES['liulanqi_key'] != liulanqi_key:
            logging.info('该用户已经在其他地方登录了，该浏览器下线')
            logout(request)
            return redirect(reverse("user:login"))

    '''所有类别'''
    types = NovelsType.objects.all()

    '''推荐'''
    indexnovels = IndexBanner.objects.all().order_by('-index')

    '''最近更新的小说'''
    update_novels = Novels.objects.filter(status=1).order_by('-update_time')[:10]

    '''最新添加'''
    add_novels = Novels.objects.filter(status=1).order_by('-add_time')[:5]

    return render(request, 'novel/index.html', locals())


# 搜索
def search(request):
    types = NovelsType.objects.all()
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if request.method == 'POST':
        searchsub = request.POST.get('searchsub')
        error_msg = ''
        if not searchsub:
            error_msg = '请输入关键词'
            return render(request, 'novel/search_result.html', {'error_msg': error_msg})
        else:
            novels_list = Novels.objects.filter(Q(name__icontains=searchsub) | Q(author__icontains=searchsub))
            # novels_author_list = Novels.objects.filter(author__icontains=searchsub)
            if novels_list:
                return render(request, 'novel/search_result.html', locals())
            else:
                return render(request, 'novel/search_result.html', {'msg': '无搜索结果'})
    return render(request, 'novel/search_result.html', locals())


# 小说详情页
def novel_detail(request, gid):
    types = NovelsType.objects.all()
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    novel = Novels.objects.get(uid=gid)
    if user:
        hits_novel = Hits.objects.filter(user_id=user.uid, novels_id=gid)
        if hits_novel:
            hits_novel = '已点赞'

    '''推荐阅读'''
    new_novels = Novels.objects.filter(type=novel.type).order_by('-add_time')[:2]

    '''最新章节'''
    new_chapter = Chapter.objects.filter(novels_id=gid).order_by('-add_time').first()

    logger.info('{}'.format(locals()))

    return render(request, 'novel/detail.html', locals())


# 小说正文
def novel_body(request, uid):
    types = NovelsType.objects.all()
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    chapter = Chapter.objects.get(uid=uid)
    # file_name = 'D:\\novels\\{}{}.txt'.format(chapter.uid,chapter.chaptername)
    file_name = 'C:\\Users\\xinxi\\PycharmProjects\\Scrapy_Novels\\novels\\novels\\file\\{}\\{}.txt'.format(chapter,
                                                                                                            chapter.chaptername)
    with open(file_name, encoding='utf-8') as file_obj:
        content = file_obj.read()
    return render(request, 'novel/novel_body.html', locals())


# 我的书架之加入书架
def add_bookrack(request):
    uid = request.GET.get('novelUid')
    novel = Novels.objects.get(uid=uid)
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    if user:
        mybookrack_novel = MyBookrack.objects.filter(user_id=user.uid, novels_id=uid, is_delete=0)
        mybookrack_novel1 = MyBookrack.objects.filter(user_id=user.uid, novels_id=uid, is_delete=1)
        if mybookrack_novel:
            return JsonResponse({'status': '402'})
        else:
            if mybookrack_novel1:
                mybookrack_novel1.update(is_delete=0)
            else:
                mybookrack = MyBookrack.objects.create(novels_id=uid, user_id=user.uid, is_delete=0)
                if mybookrack:
                    return JsonResponse({'status': '200'})
                else:
                    return JsonResponse({'status': '401'})


# 加入书签
def add_chapter(request):
    uid = request.GET.get('chapterUid')
    chapter = Chapter.objects.get(uid=uid)

    username = request.session.get('username')
    user = User.objects.filter(username=username).first()

    chapter = Chapter.objects.filter(uid=uid).first()
    novels_id = chapter.novels_id
    new_chapter = Chapter.objects.filter(novels_id=novels_id).last()
    chaptername = chapter.chaptername
    if user:
        mybookrack_chapter = MyBookrack.objects.filter(user_id=user.uid, novels_id=novels_id).first()
        logging.info('要查询的对象：{}'.format(mybookrack_chapter))
        if mybookrack_chapter:
            mybookrack_chapter.chapters_uid = uid
            mybookrack_chapter.is_delete = 0
            mybookrack_chapter.save()
            return JsonResponse({'status': '402'})
        else:
            mybookrack = MyBookrack.objects.create(chapters_uid=uid, user_id=user.uid, novels_id=novels_id, is_delete=0)
            if mybookrack:
                return JsonResponse({'status': '200'})
            else:
                return JsonResponse({'status': '401'})


# 展示我的书架
def show_bookrack(request):
    types = NovelsType.objects.all()
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    mybookrack = MyBookrack.objects.filter(user_id=user.uid, is_delete=0).all()
    count = mybookrack.count()
    print('count', count)
    novel_list = []
    chapter_list = []
    if mybookrack:
        for novel in mybookrack:
            new_chapter = Chapter.objects.filter(novels_id=novel.novels.uid).order_by('-add_time').first()
            uid = novel.chapters_uid
            chapter = Chapter.objects.filter(uid=uid).first()
            novel_list.append(new_chapter)
        dabao = zip(mybookrack, novel_list)
    return render(request, 'novel/show_bookrack.html', locals())


# 我的书架之删除
def delete_collect(request, uid):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    MyBookrack_novel = MyBookrack.objects.filter(novels_id=uid, user_id=user.uid).first()
    MyBookrack_novel.is_delete = '1'
    MyBookrack_novel.save()
    return redirect(reverse('novels:show_bookrack'))


# 小说分类展示
def category_show(request, tid):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()

    types = NovelsType.objects.all()
    type = NovelsType.objects.filter(id=tid).first()
    novels = Novels.objects.filter(type_id=tid, status=1).order_by("-add_time")

    # 分页功能
    paginator = Paginator(novels, 2)  # 每一页显示的条数
    page = request.GET.get('page', '1')  # 获取传递的页码数，默认显示为1
    try:
        page = int(page)  # page类型转换
    except Exception as err:
        page = 1
    # paginator.num_pages  # aginator.num_pages表示一共可以分的总页码数
    page_obj = paginator.page(page)  # 获取page对象
    # page_obj.has_next()  #获取下一页
    # page_obj.has_previous() #获取上一页
    # paginator.page_range
    return render(request, 'novel/category_show.html', locals())


# 点赞
def novel_hits(request):
    novel_uid = request.GET.get('novelUid')
    # novel = Novels.objects.get(uid=uid)
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    hits_novel = Hits.objects.filter(user_id=user.uid, novels_id=novel_uid)
    if hits_novel:
        hits_novel.delete()
        return JsonResponse({'status': '402'})
    else:
        uid = str(uuid.uuid4().hex)
        hits = Hits.objects.create(novels_id=novel_uid, user_id=user.uid, uid=uid)
        if hits:
            return JsonResponse({'status': '200'})
        else:
            return JsonResponse({'status': '401'})


# 排行榜单
def ranking_list(request):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    # 小说推荐列表
    indexnovels = IndexBanner.objects.all().order_by('-index')

    # 最近更新小说列表
    update_novels = Novels.objects.all().order_by('-update_time')
    return render(request, 'novel/ranking_list.html', locals())


# 全部小说
def all_novels(request):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    # 奇幻、玄幻小说
    novels1 = Novels.objects.filter(Q(type_id=1) | Q(type_id=7)).order_by('-add_time')

    # 武侠、仙侠、修真小说
    novels2 = Novels.objects.filter(Q(type_id=2) | Q(type_id=8) | Q(type_id=9)).order_by('-add_time')

    # 言情、都市小说
    novels3 = Novels.objects.filter(Q(type_id=10) | Q(type_id=3)).order_by('-add_time')

    # 历史、军事、穿越小说
    novels4 = Novels.objects.filter(Q(type_id=11) | Q(type_id=12) | Q(type_id=4)).order_by('-add_time')

    # 游戏、竞技、网游小说
    novels5 = Novels.objects.filter(Q(type_id=13) | Q(type_id=14) | Q(type_id=5)).order_by('-add_time')

    # 异灵、科幻小说
    novels6 = Novels.objects.filter(Q(type_id=15) | Q(type_id=6)).order_by('-add_time')
    return render(request, 'novel/all_novels.html', locals())


# 作者新增小说
def author_edit(request):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    types = NovelsType.objects.all()
    if request.method == 'POST':
        uid = str(uuid.uuid4().hex)
        name = request.POST.get('name')
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        author = request.POST.get('author')
        image = request.FILES.get('image')
        type_id = request.POST.get('type')
        Novels.objects.create(uid=uid, name=name, title=title, desc=desc, author=author, image=image, type_id=type_id,
                              status=0, user_id=user.uid)
        return redirect(reverse('novels:show_author_novels'))
    return render(request, 'novel/author_edit.html', locals())


# 作者发布的小说展示
def show_author_novels(request):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    novels = Novels.objects.filter(user_id=user.uid, is_delete=0).order_by('-add_time')
    return render(request, 'novel/show_author_novels.html', locals())


# 作者新增章节
def author_add_capther(request, uid):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    novel = Novels.objects.filter(uid=uid, user_id=user.uid).first()
    if request.method == 'POST':
        chapter_uid = str(uuid.uuid4().hex)
        chaptername = request.POST.get('chaptername')
        content = request.POST.get('content')
        Chapter.objects.create(uid=chapter_uid, chaptername=chaptername, novels_id=uid)
        # file_name = 'D:\\novels\\{}{}.txt'.format(chapter_uid,chaptername)
        file_name = 'C:\\Users\\xinxi\\PycharmProjects\\Scrapy_Novels\\novels\\novels\\file\\{}\\{}.txt'.format(
            novel.novels.name, chaptername)
        with open(file_name, 'w', encoding='utf-8') as file_obj:
            file_obj.write(content)
        if novel.status == '0':
            novel.status = '1'
            novel.save()
        return redirect(reverse('novels:show_author_novels'))
    return render(request, 'novel/author_add_capther.html', locals())


# 发布的小说之删除
def author_delete_novel(request, uid):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    novel = Novels.objects.filter(uid=uid, user_id=user.uid).first()
    novel.is_delete = '1'
    novel.save()
    return redirect(reverse('novels:show_author_novels'))
