# -*- coding: utf-8 -*-
# Create your views here.
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from models import Book

class BookForm(forms.ModelForm):
    isbn = forms.RegexField(regex='^[0-9]{13}$', label=u'ISBN编号')
    title = forms.CharField(max_length=200, label=u'标题')
    author = forms.CharField(max_length=200, label=u'作者')
    press = forms.CharField(max_length=200, label=u'出版社')
    sale_price = forms.FloatField(min_value=0.01, label=u'零售价')
    class Meta:
        model = Book
        exclude = ('count', 'create_at', 'update_at')

class BookSearchForm(forms.Form):
    id = forms.RegexField(required=False, regex='^[0-9]*$', label=u'编号')
    isbn = forms.CharField(required=False, max_length=13, label=u'ISBN编号')
    title = forms.CharField(required=False, max_length=200, label=u'标题')
    author = forms.CharField(required=False, max_length=200, label=u'作者')
    press = forms.CharField(required=False, max_length=200, label=u'出版社')

def index(request):
    books = Book.objects.all()
    return render_to_response('books/index.html', {
        'books':books, 
        'message': request.flash.get('message'),
        }, context_instance=RequestContext(request))

@login_required
def new(request):
    form = BookForm()
    if request.POST:
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            request.flash['message']=u'添加成功'
            return redirect(book)
    return render_to_response('books/new.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def edit(request, id):
    id = int(id)
    book = get_object_or_404(Book, pk=id)
    form = BookForm(instance=book);
    if request.POST:
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            request.flash['message']=u'保存成功'
            return redirect(book)
    return render_to_response('books/edit.html', {'form': form, 'id': id}, context_instance=RequestContext(request))

@login_required
def delete(request, id):
    id = int(id)
    book = get_object_or_404(Book, pk=id)
    book.delete()
    request.flash['message']=u'删除成功'
    return redirect(index)

@login_required
def show(request, id):
    id = int(id)
    book = get_object_or_404(Book, pk=id)
    return render_to_response('books/show.html', {'book': book, 'message': request.flash.get('message')}, context_instance=RequestContext(request))


@login_required
def search(request):
    form = BookSearchForm()
    if request.POST:
        form = BookSearchForm(request.POST)
        if form.is_valid():
            f = form.fields
            cd = form.cleaned_data
            params = u''
            message = u''
            for k in cd:
                if cd[k]:
                    add_params = u'%s=%s' % (k, cd[k])
                    add_message = u'%s包含"%s"' % (f[k].label, cd[k])
                    if params: params += '&' 
                    params += add_params
                    if message: message += u'且'
                    message += add_message
            if params: params += '&'
            params += 'message=' + message
            return redirect('/books/result/?%s' % params)
    return render_to_response('books/search.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def result(request):
    params = ''
    for k in request.GET:
        if k != 'message':
            params += '%s__contains="%s",' % (k, request.GET[k])
    query = 'Book.objects.filter(' + params +')'
    books = eval(query)
    return render_to_response('books/result.html', {'books':books, 'message':request.GET.get('message')}, context_instance=RequestContext(request))

