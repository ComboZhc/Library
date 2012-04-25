from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=200)
    discount = models.FloatField()
    create_at = models.DateTimeField(auto_now_add=True, null=False)
    update_at = models.DateTimeField(auto_now=True, null=False)
    def __unicode__(self):
        return u'%s : %s' % (self.id, self.name)