from django.conf.urls import url
from django.conf.urls import include
from .views import user

urlpatterns = [
    url(r'^index.html$', user.index),
    url(r'^base-info.html$', user.base_info),
    url(r'^tag.html$', user.tag),
    url(r'^category.html$', user.category),
    url(r'^article-(?P<article_type_id>\d+)-(?P<category_id>\d+).html$', user.article,name='article'),
    url(r'^add-article.html$', user.add_article),
    url(r'^edit-article-(\d+).html$', user.edit_article),
    url(r'^upload_avatarImg/', user.upload_avatarImg),
    url(r'^up_down_article.html$', user.up_down_article),
    url(r'^comment.html$', user.comment)
]
