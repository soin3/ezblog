#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.shortcuts import redirect
from repository import models
from django.urls import reverse
from utils.pagination import Pagination
def index(request,*args, **kwargs):
    """
    博客首页，展示全部博文

    """
    article_type_list = models.Article.type_choices
    if kwargs:
        article_type_id = int(kwargs['article_type_id'])
        base_url = reverse('index',kwargs=kwargs)
        print(base_url)
    else:
        article_type_id = None
        base_url = '/'
    data_count = article_list = models.Article.objects.filter(**kwargs).count()
    page_obj = Pagination(request.GET.get('p'),data_count)
    article_list = models.Article.objects.filter(**kwargs).order_by('-nid')[page_obj.start:page_obj.end]
    comment_list = models.Article.objects.filter(**kwargs).order_by('comment_count')
    page_str = page_obj.page_str(base_url)
    return render(
        request,
        'index.html',
        {
            'article_list': article_list,
            'article_type_id': article_type_id,
            'article_type_list': article_type_list,
            'page_str': page_str,
            'command_list':comment_list
        }
    )


def home(request, site):
    """
    博主个人首页
    :param request:
    :param site: 博主的网站后缀如：http://xxx.com/wupeiqi.html
    :return:
    """
    #user_home = models.Blog.objects.filter(site=site).select_related('user').first()
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    follower = models.UserFans.objects.filter(follower_id=blog.user.nid).count()
    tag_list = models.Tag.objects.filter(blog=blog).all()
    category_list = models.Category.objects.filter(blog=blog)
    article_list = models.Article.objects.filter(blog=blog).all()
    date_list = models.Article.objects.raw('select nid,count(nid) as num,DATE_FORMAT(create_time,"%%Y年%%m月") as ctime from repository_article group by DATE_FORMAT(create_time,"%%Y年%%m月")')
    # for item in date_list:
    #     print(item.num,item.ctime)

    if not blog:
        redirect("/")

    return render(request, 'home.html', {'blog': blog,'follower':follower,'tag_list':tag_list,
                                         'category_list':category_list,'article_list': article_list,
                                         'date_list':date_list
                                         })


def filter(request, site, condition, val):
    """
    分类显示
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    follower = models.UserFans.objects.filter(follower_id=blog.user.nid).count()
    tag_list = models.Tag.objects.filter(blog=blog).all()
    category_list = models.Category.objects.filter(blog=blog)
    date_list = models.Article.objects.raw('select nid,count(nid) as num,DATE_FORMAT(create_time,"%%Y年%%m月") as ctime from repository_article group by DATE_FORMAT(create_time,"%%Y年%%m月")')
    # for item in date_list:
    #     print(item.num,item.ctime)

    if not blog:
        redirect("/")

    template_name = "home_summary_list.html"
    if condition == 'tag':
        template_name = "home_title_list.html"
        article_list = models.Article.objects.filter(tags__nid=val, blog=blog).all()
    elif condition == 'category':
        article_list = models.Article.objects.filter(category__nid=val, blog=blog).all()
    elif condition == 'date':
        article_list = models.Article.objects.filter(blog=blog).extra(
            where=['date_format(create_time,"%%Y年%%m月")=%s'], params=[val, ]).all()
    else:
        article_list = []

    return render(request,template_name, {'blog': blog,'follower':follower,'tag_list':tag_list,
                                         'category_list':category_list,'article_list': article_list,
                                         'date_list':date_list,'template_name':template_name
                                         })


def detail(request, site, nid):
    """
    博文详细页

    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    tag_list = models.Tag.objects.filter(blog=blog).all()
    category_list = models.Category.objects.filter(blog=blog)
    date_list = models.Article.objects.raw('select nid,count(nid) as num,DATE_FORMAT(create_time,"%%Y年%%m月") as ctime from repository_article group by DATE_FORMAT(create_time,"%%Y年%%m月")')
    article = models.Article.objects.filter(blog=blog,nid=nid).select_related('category', 'articledetail').first()
    # comment_list = models.Comment.objects.filter(article_id=nid).all()
    base_url = '/%s/%s.html'%(site,nid)
    data_count  = models.Comment.objects.filter(article_id=nid).count()
    page_obj = Pagination(request.GET.get('p'),data_count)
    comment_list = models.Comment.objects.filter(article_id=nid).order_by('-nid')[page_obj.start:page_obj.end]
    page_str = page_obj.page_str(base_url)

    return render(request, 'home_detail.html',{
        "blog":blog,
        "tag_list":tag_list,
        "category_list":category_list,
        "date_list":date_list,
        "article":article,
        "comment_list":comment_list,
        "page_str":page_str})

