from django.conf.urls import url
from django.contrib.staticfiles.views import serve
from django.urls import path, include

from Qinxiangshuge.settings import MEDIA_ROOT
from novels.views import *

app_name = 'novels'

urlpatterns = [
    url(r'media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    url(r'^tinymce/', include('tinymce.urls')),
    path('index', index, name='index'),
    path('search', search, name='search'),
    path('detail/<str:gid>', novel_detail, name='detail'),
    path('novelbody/<str:uid>', novel_body, name='novelbody'),
    path('add_bookrack', add_bookrack, name='add_bookrack'),
    path('show_bookrack', show_bookrack, name='show_bookrack'),
    path('add_chapter', add_chapter, name='add_chapter'),
    path('delete_collect/<str:uid>', delete_collect, name='delete_collect'),
    path('category_show/<str:tid>', category_show, name='category_show'),
    path('novel_hits', novel_hits, name='novel_hits'),
    path('all_novels', all_novels, name='all_novels'),
    path('ranking_list', ranking_list, name='ranking_list'),
    path('author_edit', author_edit, name='author_edit'),
    path('author_add_capther/<str:uid>', author_add_capther, name='author_add_capther'),
    path('show_author_novels', show_author_novels, name='show_author_novels'),
    path('author_delete_novel/<str:uid>', author_delete_novel, name='author_delete_novel'),
]
