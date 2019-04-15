from django.db import models


class UserInfo(models.Model):
    """
    用户表
    """
    nid = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=64)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    avatar = models.ImageField(verbose_name='头像')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    fans = models.ManyToManyField(verbose_name='粉丝们', to='UserInfo', through='UserFans',
                                  through_fields=('user', 'follower'))

class Blog(models.Model):
    """
    博客信息
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客前缀', max_length=32, unique=True)
    theme = models.ForeignKey(verbose_name='个人博客主题', to='Blog_Theme', to_field='nid', related_name='themes',on_delete=models.CASCADE)
    motto = models.CharField(verbose_name='个人博客座右铭', max_length=256,blank=True)
    user = models.OneToOneField(to='UserInfo', to_field='nid',on_delete=models.CASCADE,)

class Blog_Theme(models.Model):
    """
    博客主题
    """
    nid = models.BigAutoField(primary_key=True)
    name = models.CharField(verbose_name='主题模板名称', max_length=64)
    theme_name = models.CharField(verbose_name='主题展示名称', max_length=64)


class UserFans(models.Model):
    """
    互粉关系表
    """
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users',on_delete=models.CASCADE,)
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers',on_delete=models.CASCADE,)

    class Meta:
        unique_together = [
            ('user', 'follower'),
        ]


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid',on_delete=models.CASCADE,)


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    content = models.TextField(verbose_name='文章内容', )

    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid',on_delete=models.CASCADE,)


class UpDown(models.Model):
    """
    文章顶或踩
    """
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid',on_delete=models.CASCADE,)
    user = models.ForeignKey(verbose_name='赞或踩用户', to='UserInfo', to_field='nid',on_delete=models.CASCADE,)
    up = models.BooleanField(verbose_name='是否赞')

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey(verbose_name='回复评论', to='self', related_name='back', null=True,on_delete=models.CASCADE,)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid',on_delete=models.CASCADE,)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid',on_delete=models.CASCADE,)


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid',on_delete=models.CASCADE,)


class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章简介', max_length=255)
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid',on_delete=models.CASCADE,)
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True,on_delete=models.CASCADE,)

    type_choices = [
        (1, "python"),
        (2, "java"),
        (3, "c++"),
        (4, "php"),
        (5, "shell"),
    ]

    article_type_id = models.IntegerField(choices=type_choices, default=None)

    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )


class Article2Tag(models.Model):
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid',on_delete=models.CASCADE,)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid',on_delete=models.CASCADE,)

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]



