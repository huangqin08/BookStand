from django.contrib import admin

from novels.models import NovelsType, Novels, ViceNovels, IndexBanner,Chapter

admin.site.register(NovelsType)
admin.site.register(Novels)
admin.site.register(ViceNovels)
admin.site.register(IndexBanner)
admin.site.register(Chapter)
