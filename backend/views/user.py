#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render,HttpResponse,redirect
from ..auth.auth import check_login
from ..forms.article import ArticleForm
from repository import models
from web import forms
from web.views.account import JsonCunstomEncode
import json
from utils.pagination import Pagination
from django.urls import reverse
from django.db import transaction
from utils.xss import XSSFilter

@check_login
def index(request):
    """
    博主管理首页

    """
    user_obj = models.UserInfo.objects.filter(nid=str(request.session.get('user_info')["nid"])).first()
    return render(request, 'backend_index.html',{"user_obj":user_obj})
@check_login
def base_info(request):
    """
    博主管理个人信息

    """
    user_obj = models.UserInfo.objects.filter(nid=str(request.session.get('user_info')["nid"])).first()
    blog_theme_obj = models.Blog_Theme.objects.all()
    blog_obj=models.Blog.objects.filter(user_id=str(request.session.get('user_info')["nid"]))
    ret={"status":False,"error":None,"data":None}
    if request.method =='GET':
        return render(request, 'backend_base_info.html',{"user_obj":user_obj,"blog_theme_obj":blog_theme_obj,"blog_obj":blog_obj})
    elif request.method == "POST":
        ret={"status":False,"error":None,"data":None}
        form_obj = forms.Base_info_Form(request.POST)
        if form_obj.is_valid():
                ret["status"]=True
                models.UserInfo.objects.filter(nid=str(request.session.get('user_info')["nid"])).update(nickname=str(request.POST.get("nickname")))
                blog_obj.update(theme_id=int(request.POST.get("blogTheme")),motto=str(request.POST.get("motto")))
        else:
                ret["error"]=form_obj.errors.as_data()
        result=json.dumps(ret,cls=JsonCunstomEncode)
        #不能使用render，使用render返回数据,前端var data1=JSON.parse(arg)转换报错。可以使用HttpResponse直接返回数据
        #return render(request, 'register.html',{"result":result})
        return HttpResponse(result)

@check_login
def tag(request):
    """
    博主个人标签管理
    """
    #用户对象
    user_obj = models.UserInfo.objects.filter(nid=str(request.session.get('user_info')["nid"])).first()
    #博客对象
    blog = models.Blog.objects.filter(site=user_obj.username).select_related('user').first()
    #分页
    base_url = '/backend/tag.html'
    tag_count = article_list = models.Tag.objects.filter(blog_id=blog.nid).count()
    page_obj = Pagination(request.GET.get('p'),tag_count)
    page_str = page_obj.page_str(base_url)
    #标签对象
    tag_list = models.Tag.objects.filter(blog=blog).all().order_by('nid')[page_obj.start:page_obj.end]
    ret={"status":False,"error":None,"data":None}
    if request.method =='GET':
        return render(request, 'backend_tag.html',{"user_obj":user_obj,"tag_list":tag_list,"page_str":page_str})
    elif request.method == "POST":
        ret["status"]=True
        if request.POST.get("tag_type") == "delete":
            tag_id = request.POST.get("tag_id")
            models.Tag.objects.filter(nid=tag_id).delete()
        elif request.POST.get("tag_type") == "save":
            tag_id = request.POST.get("tag_id")
            tag_name = request.POST.get("tag_name")
            models.Tag.objects.filter(nid=tag_id).update(title=tag_name)
        else:
            tag_name = request.POST.get("tag_name")
            models.Tag.objects.create(title=tag_name,blog_id=blog.nid)
        return HttpResponse(json.dumps(ret))

@check_login
def category(request):
    """
    博主个人分类管理
    """
    #用户对象
    user_obj = models.UserInfo.objects.filter(nid=str(request.session.get('user_info')["nid"])).first()
    #博客对象
    blog = models.Blog.objects.filter(site=user_obj.username).select_related('user').first()
    #分页
    base_url = '/backend/category.html'
    category_count = article_list = models.Category.objects.filter(blog_id=blog.nid).count()
    page_obj = Pagination(request.GET.get('p'),category_count)
    page_str = page_obj.page_str(base_url)
    #分类对象
    category_list = models.Category.objects.filter(blog=blog).all().order_by('nid')[page_obj.start:page_obj.end]
    ret={"status":False,"error":None,"data":None}
    if request.method =='GET':
        return render(request, 'backend_category.html',{"user_obj":user_obj,"blog":blog,"category_list":category_list,"page_str":page_str})
    elif request.method == "POST":
        ret["status"]=True
        if request.POST.get("category_type") == "delete":
            category_id = request.POST.get("category_id")
            models.Article.objects.filter(category_id=category_id).update(category_id='')
            models.Category.objects.filter(nid=category_id).delete()
        elif request.POST.get("category_type") == "save":
            category_id = request.POST.get("category_id")
            category_name = request.POST.get("category_name")
            models.Category.objects.filter(nid=category_id).update(title=category_name)
        else:
            category_name = request.POST.get("category_name")
            models.Category.objects.create(title=category_name,blog_id=blog.nid)
        return HttpResponse(json.dumps(ret))

@check_login
def article(request,*args, **kwargs):
    """
    博主个人文章管理

    """
    user_obj = models.UserInfo.objects.filter(nid=str(request.session.get('user_info')["nid"])).first()
    blog_id = request.session.get("user_info")["blog__nid"]
    condition = {}
    for k, v in kwargs.items():
        if v == '0':
            pass
        else:
            condition[k] = v
    condition['blog_id'] = blog_id
    data_count = models.Article.objects.filter(**condition).count()
    page = Pagination(request.GET.get('p', 1), data_count)
    result = models.Article.objects.filter(**condition).order_by('-nid').only('nid', 'title','blog').select_related('blog')[page.start:page.end]
    page_str = page.page_str(reverse('article', kwargs=kwargs))
    category_list = models.Category.objects.filter(blog_id=blog_id).values('nid', 'title')
    type_list = map(lambda item: {'nid': item[0], 'title': item[1]}, models.Article.type_choices)
    kwargs['p'] = page.current_page
    ret={"status":False,"error":None,"data":None}
    if request.method == 'GET':
        return render(request,
                      'backend_article.html',
                      {'result': result,
                       'user_obj':user_obj,
                       'page_str': page_str,
                       'category_list': category_list,
                       'type_list': type_list,
                       'arg_dict': kwargs,
                       'data_count': data_count
                       }
                      )
    elif request.method == "POST":
        ret["status"]=True
        models.Article.objects.filter(nid=request.POST.get("article_id")).delete()
        return HttpResponse(json.dumps(ret))

def add_article(request):
    """
    添加文章
    """
    if request.method == 'GET':
        form = ArticleForm(request=request)
        return render(request, 'backend_add_article.html', {'form': form})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                tags = form.cleaned_data.pop('tags')
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                form.cleaned_data['blog_id'] = request.session['user_info']['blog__nid']
                obj = models.Article.objects.create(**form.cleaned_data)
                models.ArticleDetail.objects.create(content=content, article=obj)
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            return render(request, 'backend_add_article.html', {'form': form})
    else:
        return redirect('/')


def edit_article(request,nid):
    """
    编辑文章

    """
    blog_id = request.session['user_info']['blog__nid']
    if request.method == 'GET':
        obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
        if not obj:
            return render(request, 'backend_no_article.html')
        tags = obj.tags.values_list('nid')
        if tags:
            tags = list(zip(*tags))[0]
        init_dict = {
            'nid': obj.nid,
            'title': obj.title,
            'summary': obj.summary,
            'category_id': obj.category_id,
            'article_type_id': obj.article_type_id,
            'content': obj.articledetail.content,
            'tags': tags
        }
        form = ArticleForm(request=request, data=init_dict)
        return render(request, 'backend_edit_article.html', {'form': form, 'nid': nid})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
            if not obj:
                return render(request, 'backend_no_article.html')
            with transaction.atomic():
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                tags = form.cleaned_data.pop('tags')
                models.Article.objects.filter(nid=obj.nid).update(**form.cleaned_data)
                models.ArticleDetail.objects.filter(article=obj).update(content=content)
                models.Article2Tag.objects.filter(article=obj).delete()
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            return render(request, 'backend_edit_article.html', {'form': form, 'nid': nid})

def upload_avatarImg(request):
    """
    上传预览头像
    """
    if request.method == "POST":
        username = request.POST.get('username')
        img = request.FILES.get('avatarImg')
        import os
        avatar_filepath='static/imgs/avatar/'+str(request.session.get('user_info')['username'])+'/'
        if  os.path.exists(avatar_filepath):
            pass
        else:
            os.makedirs(avatar_filepath)
        img_path = os.path.join(avatar_filepath,img.name)
        print(img_path)
        obj = models.UserInfo.objects.filter(nid=str(request.session.get('user_info')["nid"])).update(avatar=img_path)
        with open(img_path,'wb') as f:
            for item in img.chunks():
                f.write(item)
        ret = {'code': True , 'data': img_path}
        return HttpResponse(json.dumps(ret))
@check_login
def up_down_article(request):
    ret={"status":False,"error":None,"data":None}
    if request.method == "POST":
        user_id = request.session.get('user_info')["nid"]
        article_id = request.POST.get("article_id")
        up = request.POST.get("like_type")
        if up == '0':
            up_obj = models.UpDown.objects.filter(article_id=article_id,user_id=user_id,up=0)
            updown_obj = models.UpDown.objects.filter(article_id=article_id,user_id=user_id)
            if updown_obj:
                ret["error"]="你已经踩过或者点赞啦！"
                return HttpResponse(json.dumps(ret))
            elif up_obj:
                ret["error"]="点赞和踩不能同时哦！"
                return HttpResponse(json.dumps(ret))
            else:
                ret["status"]=True
                models.UpDown.objects.create(up=0,article_id=article_id,user_id=user_id)
                up_count=int(models.Article.objects.filter(nid=article_id).first().up_count)+1
                models.Article.objects.filter(nid=article_id).update(up_count=up_count)
                return HttpResponse(json.dumps(ret))
        else:
            updown_obj = models.UpDown.objects.filter(article_id=article_id,user_id=user_id)
            down_obj = models.UpDown.objects.filter(article_id=article_id,user_id=user_id,up=1)
            if updown_obj:
                ret["error"]="你已经踩过或者点赞啦！"
                return HttpResponse(json.dumps(ret))
            elif down_obj:
                ret["error"]="点赞和踩不能同时哦！"
                return HttpResponse(json.dumps(ret))
            else:
                ret["status"]=True
                models.UpDown.objects.create(up=1,article_id=article_id,user_id=user_id)
                down_count=int(models.Article.objects.filter(nid=article_id).first().down_count)+1
                models.Article.objects.filter(nid=article_id).update(down_count=down_count)
                return HttpResponse(json.dumps(ret))

@check_login
def comment(request):
    ret={"status":False,"error":None,"data":None}
    if request.method == "POST":
        print(request.POST)
        reply_id = request.POST.get("to_user_id")
        content = request.POST.get("content")
        article_id = request.POST.get("article_id")
        user_id = request.session['user_info']["nid"]
        models.Comment.objects.create(content=content,reply_id=reply_id,article_id=article_id,user_id=user_id)
        comment_count=int(models.Article.objects.filter(nid=article_id).first().comment_count)+1
        models.Article.objects.filter(nid=article_id).update(comment_count=comment_count)
        ret["status"]=True
        return HttpResponse(json.dumps(ret))
