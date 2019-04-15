__author__ = 'solin'
from django.forms import widgets, fields,ValidationError
from django import forms
from repository import models

class RegForm(forms.Form):
    username = forms.CharField(max_length=15, min_length=5, error_messages={"required": "*用户名不能为空","max_length": "*长度不能大于15",
            "min_length": "*长度不能小于5", },
                               widget=widgets.TextInput(
                                   attrs={"class": "form-control",
                                          "placeholder": "用户名长度不能小于5大于15"
                                   }))
    password = forms.CharField(min_length=6, max_length=25,error_messages={"required": "*密码不能为空",'min_length': '*密码长度大于6位' }, widget=widgets.PasswordInput(
        attrs={"class": "form-control",
               "placeholder": "密码不能为纯数字,字母且长度大于6位"
        }))
    confirm_password = forms.CharField(min_length=6, error_messages={"required": "*密码不能为空", 'min_length': '*密码长度大于6位'},
                                 widget=widgets.PasswordInput(attrs={"class": "form-control", "placeholder": "再次输入密码"}))
    email = forms.EmailField(error_messages={"required": "*邮箱不能为空",'invalid': '*邮箱格式错误' },
                             widget=widgets.EmailInput(attrs={"class": "form-control", "placeholder": "邮箱"}))
    very_code = fields.CharField(error_messages={"required": "验证码不能为空"},
                                  widget=widgets.Input(attrs={"class": "form-control"}))


    def clean_username(self):
        #验证用户存不存在
        #print(self.cleaned_data["username"])
        obj = models.UserInfo.objects.filter(username=self.cleaned_data["username"])
        if not obj:
            #print(self.cleaned_data["username"])
            return self.cleaned_data["username"]
        else:
            raise ValidationError("*用户名已存在")
    def clean_email(self):
         obj = models.UserInfo.objects.filter(email=self.cleaned_data["email"])
         if not obj:
            #print(self.cleaned_data["username"])
            return self.cleaned_data["email"]
         else:
            raise ValidationError("*邮箱已存在")

    def clean_password(self):
        '''验证密码是否合法'''
        data = self.cleaned_data.get("password")
        if not data.isdigit():
            return self.cleaned_data.get("password")
        else:
            raise ValidationError("*密码不能全是数字")

    def clean(self):
        if self.cleaned_data.get("password") == self.cleaned_data.get(
        "confirm_password"):
            return self.cleaned_data
        else:
            raise ValidationError("*两次密码不一致")

class Base_info_Form(forms.Form):
    nickname = forms.CharField(max_length=15, error_messages={"required": "*昵称不能为空","max_length": "*昵称长度不能大于15" })
    motto = forms.CharField(max_length=256, error_messages={"required": "*座右铭不能为空","max_length": "*座右铭字数太长", })


