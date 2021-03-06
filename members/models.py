# -*- coding: utf-8 -*-
from django.db import models
from groups.models import Group

def topup_point(amount):
    return int(amount / 2)

class Member(models.Model):
    GENDER_CHOICES = (
        ('M', u'男'),
        ('F', u'女'),
    )
    GENDER_CHOICES_WITH_EMPTY = (
        ('', u'不限'),
        ('M', u'男'),
        ('F', u'女'),
    )
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=128)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField()
    valid_to = models.DateField()
    valid = models.BooleanField()
    identify_number = models.CharField(max_length=18)
    point = models.IntegerField(default=0)
    balance = models.FloatField(default=0)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, related_name = 'members')
    create_at = models.DateTimeField(auto_now_add=True, null=False)
    update_at = models.DateTimeField(auto_now=True, null=False)
    def __unicode__(self):
        return u'%s<%s>' % (self.name, self.gender)
    def get_absolute_url(self):
        return "/members/%i/show/" % self.id
    def set_password(self, raw_password):#使用sha1算法加密密码串
        import random
        from django.contrib.auth.models import get_hexdigest
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)
        self.save()
    def check_password(self, raw_password):#检查密码是否匹配
        from django.contrib.auth.models import check_password
        return check_password(raw_password, self.password)
    def topup(self, amount):#为此会员充值
        from topups.models import Topup
        topup = Topup()
        topup.member = self
        topup.amount = amount
        topup.save()
        self.balance += amount
        self.point += topup_point(amount)
        self.save()
    class Meta:
        ordering = ['-create_at']#指定默认排序方式为按时间降序
        