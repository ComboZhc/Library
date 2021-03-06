# -*- coding: utf-8 -*-
# Create your views here.
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from models import Member
from groups.models import Group
from helper import helper
from histories.models import History

class MemberForm(forms.ModelForm):#添加新会员的表单结构
    name = forms.CharField(max_length=200, label=u'姓名')
    password = forms.CharField(max_length=16, label=u'密码', widget=forms.PasswordInput)
    gender = forms.ChoiceField(choices=Member.GENDER_CHOICES, label=u'性别')
    birthday = forms.DateField(widget=forms.DateInput, label=u'生日')
    valid_to = forms.DateField(widget=forms.DateInput, label=u'有效期至')
    valid = forms.BooleanField(required=False, widget=forms.CheckboxInput, label=u'是否有效')
    identify_number = forms.RegexField(regex='^[0-9]{18}$', label=u'身份证')
    group = forms.ModelChoiceField(required=False, queryset=Group.objects.all(), label=u'会员组')
    def save(self):
        super(MemberForm, self).save()  
        d = self.cleaned_data
        m = self.instance
        m.set_password(d['password'])
        m.save()
        return m
    class Meta:
        model = Member
        exclude = ('password', 'balance', 'point', 'create_at', 'update_at')
        
class MemberEditForm(forms.ModelForm):#编辑会员的表单结构
    name = forms.CharField(max_length=200, label=u'姓名')
    password = forms.CharField(max_length=16, label=u'密码验证', widget=forms.PasswordInput)
    gender = forms.ChoiceField(choices=Member.GENDER_CHOICES, label=u'性别')
    birthday = forms.DateField(widget=forms.DateInput, label=u'生日')
    valid_to = forms.DateField(widget=forms.DateInput, label=u'有效期至')
    valid = forms.BooleanField(required=False, widget=forms.CheckboxInput, label=u'是否有效')
    identify_number = forms.RegexField(regex='^[0-9]{18}$', label=u'身份证')
    group = forms.ModelChoiceField(required=False, queryset=Group.objects.all(), label=u'会员组')
    def clean_password(self):
        d = self.cleaned_data
        m = self.instance
        if not m.check_password(d['password']):
            raise ValidationError(u'密码不正确')
        return d['password']
    class Meta:
        model = Member
        exclude = ('password', 'balance', 'point', 'create_at', 'update_at')
        
class MemberChangePasswordForm(forms.Form):#修改密码的表单结构
    password = forms.CharField(max_length=16, label=u'原密码', widget=forms.PasswordInput)
    new_password = forms.CharField(max_length=16, label=u'新密码', widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(max_length=16, label=u'新密码确认', widget=forms.PasswordInput)
    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        super(MemberChangePasswordForm, self).__init__(*args, **kwargs)
    def clean(self):
        d = self.cleaned_data
        m = self.instance
        if not m.check_password(d['password']):
            raise ValidationError(u'密码不正确')
        if (cmp(d['new_password'], d['new_password_confirm']) != 0):
            raise ValidationError(u'两次密码不一致')
        return d
    def save(self):        
        d = self.cleaned_data
        m = self.instance
        m.set_password(d['new_password'])
        m.save()
        return m
    
class MemberSearchForm(forms.Form):#搜索会员的表单结构
    id = forms.RegexField(required=False, regex='^[0-9]*$', label=u'编号')
    name = forms.CharField(required=False, max_length=200, label=u'姓名')
    gender = forms.TypedChoiceField(required=False, choices=Member.GENDER_CHOICES_WITH_EMPTY, label=u'性别')
    birthday = forms.DateField(required=False, widget=forms.DateInput, label=u'生日')
    identify_number = forms.CharField(required=False, max_length=18, label=u'身份证')
    
class MemberTopupForm(forms.Form):#充值的表单结构
    password = forms.CharField(max_length=16, label=u'密码', widget=forms.PasswordInput)
    amount = forms.FloatField(min_value=0, label=u'金额')
    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        super(MemberTopupForm, self).__init__(*args, **kwargs)
    def clean_password(self):
        p = self.cleaned_data['password']
        m = self.instance
        if not m.check_password(p):
            raise ValidationError(u'密码不正确')
        return p
    def save(self):        
        d = self.cleaned_data
        m = self.instance
        m.topup(d['amount'])
        m.save()
        return m

def add_history(user, content, topup, link):#记录与会员相关的事件
    if link:
        History(user=user, content=content, klass='Member', unicode=topup, url=topup.get_absolute_url()).save()
    else:
        History(user=user, content=content, klass='Member', unicode=topup).save()

def index(request):#会员列表
    members = Member.objects.all()
    return render_to_response('members/index.html', {'members':members, 'message': request.flash.get('message')}, context_instance=RequestContext(request))

@login_required
def new(request):#添加新会员
    form = MemberForm()
    if request.POST:
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            request.flash['message']=u'添加成功'
            add_history(request.user, u'添加会员', member, True)
            return redirect(member)
    return render_to_response('members/new.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def edit(request, id):#编辑指定会员
    id = int(id)
    member = get_object_or_404(Member, pk=id)
    form = MemberEditForm(instance=member);
    if request.POST:
        form = MemberEditForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            request.flash['message']=u'保存成功'
            add_history(request.user, u'编辑会员', member, True)
            return redirect(member)
    return render_to_response('members/edit.html', {'form': form, 'id': id}, context_instance=RequestContext(request))

@login_required
def delete(request, id):#删除指定会员
    id = int(id)
    member = get_object_or_404(Member, pk=id)
    member.delete()
    request.flash['message']=u'删除成功'
    add_history(request.user, u'删除会员', member, False)
    return redirect(index)

@login_required
def show(request, id):#显示指定会员详细信息
    id = int(id)
    member = get_object_or_404(Member, pk=id)
    return render_to_response('members/show.html', {'member': member, 'message': request.flash.get('message')}, context_instance=RequestContext(request))

@login_required
def change_password(request, id):#更改密码
    id = int(id)
    member = get_object_or_404(Member, pk=id)
    form = MemberChangePasswordForm(member)
    if request.POST:
        form = MemberChangePasswordForm(member, request.POST)
        if form.is_valid():
            form.save()
            request.flash['message']=u'密码修改成功'
            History(user=request.user, content=u'修改会员#%d密码.' % member.id).save()
            return redirect(member)
    return render_to_response('members/change_password.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def topup(request, id):#会员充值
    id = int(id)
    member = get_object_or_404(Member, pk=id)
    form = MemberTopupForm(member)
    if request.POST:
        form = MemberTopupForm(member, request.POST)
        if form.is_valid():
            form.save()
            request.flash['message']=u'充值成功'
            add_history(request.user, u'会员充值', member, False)
            return redirect(member)
    return render_to_response('members/topup.html', {'member': member,'form': form}, context_instance=RequestContext(request))

@login_required
def search(request):#搜索会员
    form = MemberSearchForm()
    if request.POST:
        form = MemberSearchForm(request.POST)
        if form.is_valid():
            d = {}
            for k, v in form.cleaned_data.iteritems():
                if v:
                    d[k] = v
            d['message'] = helper.get_search_message(form.fields, d)
            return redirect(helper.url_with_querystring(reverse(result), d))
    return render_to_response('members/search.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def result(request):#执行会员搜索
    params = ''
    fields = MemberSearchForm().fields
    for k in request.GET:
        if k in fields:
            params += '%s__contains="%s",' % (k, request.GET[k])
    query = 'Member.objects.filter(' + params +')'
    members = eval(query)
    return render_to_response('members/result.html', {'members':members, 'message':request.GET.get('message')}, context_instance=RequestContext(request))

