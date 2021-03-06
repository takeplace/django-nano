# -*- coding: UTF-8 -*-
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from nano.tools.models import AbstractText

class PMManager(models.Manager):

    def sent(self, user):
        """Limit to PMs sent by <user>"""

        return self.get_query_set().filter(
                sender=user, 
                sender_deleted=False)

    def archived(self, user):
        """Limit to PMs received and archived by <user>"""

        return self.get_query_set().filter(
                recipient=user,
                recipient_deleted=False,
                recipient_archived=True
                )

    def received(self, user):
        """Limit to PMs received by <user>"""

        return self.get_query_set().filter(
                recipient=user,
                recipient_archived=False, 
                recipient_deleted=False
                )

class PM(AbstractText):
    subject = models.CharField(max_length=64, blank=True, default='')
    sent = models.DateTimeField(default=datetime.now, editable=False)
    sender = models.ForeignKey(User, related_name='pms_sent')
    sender_deleted = models.BooleanField(default=False)
    recipient = models.ForeignKey(User, related_name='pms_received')
    recipient_archived = models.BooleanField(default=False)
    recipient_deleted = models.BooleanField(default=False)

    objects = PMManager()

    #assert False, 'tii'

    class Meta:
        db_table = 'nano_privmsg_pm'

    def __unicode__(self):
        if self.subject:
            return self.subject
        else:
            return self.content[:64]

    def save(self, *args, **kwargs):
        if not self.subject:
            snippet = self.text[:64]
            ls = len(snippet)
            if ls == 64 and ls < len(self.text):
                snippet = snippet[:-1] + u'…'
            self.subject = snippet
        super(PM, self).save(*args, **kwargs)

    def delete(self):
        if self.is_deleted():
            super(PM, self).delete()

#     @models.permalink
#     def get_absolute_url(self):
#         return ('show_pms', (), {'msgid': self.id, 'uid':}
#         )

    def is_deleted(self):
        if self.sender_deleted and self.recipient_deleted:
            return True
        if (self.sender_deleted or self.recipient_deleted) and self.sender == self.recipient:
            return True
        return False

