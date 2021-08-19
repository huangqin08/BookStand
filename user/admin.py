from django.contrib import admin
from user.models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    #设置用户显示
    list_display = ['username','phone_num','first_name','last_name','date_joined']

admin.site.register(User,UserAdmin)
