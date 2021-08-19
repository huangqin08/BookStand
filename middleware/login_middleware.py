from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

loginRequired_list = ['/novels/show_bookrack', '/novels/author_edit', '/novels/show_author_novels',
                      '/novels/novel_hits', '/novels/add_bookrack', '/novels/add_chapter',]


class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):  # ------>进入视图函数之前调用动作，如用户登录，IP拦截，缓存
        if request.path in loginRequired_list:
            user = request.session.get('username')
            if not user:
                if request.is_ajax():
                    return JsonResponse({'status': '400'})
                else:
                    return redirect(reverse('user:login'))

    # def process_response(self,request,response):  #----->视图函数执行完毕之后调用方法，这个函数一定要返回response
    #     response.set_cookie('test','abc')
    #     return response
    #
    # def process_exception(self,request,exception):    #------>只要有python异常调用函数
    #     return render(request,'500error.html')
    #
    # def process_view(self,request,callback,callback_args,callback_kwargs):  #在进入视图函数之前
    #     callback(request) #视图函数对象，传人request，相当于调用了视图函数
    #
    # def process_template_response(self,request,response):   #模板渲染时
    #     pass
