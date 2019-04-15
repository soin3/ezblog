#!/usr/bin/env python
# -*- coding:utf-8 -*-
from io import BytesIO
from django.shortcuts import HttpResponse
from django.shortcuts import render,redirect
from utils.check_code import create_validate_code
from web import forms
from repository import models
import json,hashlib
from django.core.exceptions import ValidationError
class JsonCunstomEncode(json.JSONEncoder):
    def default(self, field):
        if isinstance(field,ValidationError):
            return {"code":field.code,"message":field.message}
        else:
            return json.JSONEncoder.default(self,field)

def check_code(request):
    """
        验证码
    """
    stream = BytesIO()
    img, code = create_validate_code()
    img.save(stream, 'PNG')
    request.session['CheckCode'] = code
    return HttpResponse(stream.getvalue())


def login(request):
    """
    登陆
    """
    ret={"status":False,"error":None,"data":None}
    if request.method =='GET':
        return render(request, 'login.html')
    elif request.method == "POST":
        print(request.POST)
        ret={"status":False,"error":None,"data":None}
        if request.session['CheckCode'].upper() == request.POST.get('check_code').upper():
            username = request.POST.get('username')
            password = request.POST.get('password')
            md5 = hashlib.md5()
            md5.update(password.encode('utf-8'))     #注意转码
            md5_passwd = md5.hexdigest()
            obj = models.UserInfo.objects.filter(username=username,password=md5_passwd).\
                values('nid', 'nickname',
                       'username', 'email',
                       'avatar',
                       'blog__nid',
                       'blog__site').first()
            if obj:
                ret["status"]=True
                request.session["user_info"]=obj
                if request.POST.get('rmb'):
                    #设置session超时时间
                    request.session.set_expiry(60 * 60 * 24 * 7)
            else:
                ret["error"]="*用户名或密码错误"
        else:
            ret["error"]="*验证码错误"

        result=json.dumps(ret,cls=JsonCunstomEncode)
        return HttpResponse(result)



def register(request):
    """
    注册
    :param request:
    :return:
    """
    ret={"status":False,"error":None,"data":None}
    if request.method == "GET":
        return render(request, "register.html")
    elif  request.method == "POST":
        if request.session['CheckCode'].upper() == request.POST.get('very_code').upper():
            form_obj = forms.RegForm(request.POST)
            if form_obj.is_valid():
                ret["status"]=True
                ret["data"]=form_obj.cleaned_data
                username=ret["data"].get("username")
                password=ret["data"].get("password")
                email= ret["data"].get("email")
                nickname = ret["data"].get("username")
                md5 = hashlib.md5()
                md5.update(password.encode('utf-8'))     #注意转码
                res = md5.hexdigest()
                #添加用户
                user=models.UserInfo.objects.create(username = username,password=res,nickname=nickname,email=email,avatar="static/imgs/avatar/default.png")
                user.save()
                #默认开通博客
                blogtitle=username+"的博客"
                blog=models.Blog.objects.create(title=blogtitle,site=username,theme_id=1,user_id=user.nid)
                blog.save()
            else:
                ret["error"]=form_obj.errors.as_data()
        else:
            ret["error"]= "*验证码错误"
        result=json.dumps(ret,cls=JsonCunstomEncode)
        #不能使用render，使用render返回数据,前端var data1=JSON.parse(arg)转换报错。可以使用HttpResponse直接返回数据
        #return render(request, 'register.html',{"result":result})
        return HttpResponse(result)

def register_welcome(request):
    '''注册成功'''
    return render(request, "register_welcome.html")

def logout(request):
    """
    注销
    """
    request.session.clear()
    return redirect('/')




