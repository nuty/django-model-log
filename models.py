# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.encoding import force_text, smart_unicode

from .helpers import ACTION_CHOICE
from django.db.models.signals import post_save


class DirtyFieldsMixin(object):

    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(reset_state, sender=self.__class__,
                            dispatch_uid='%s-DirtyFieldsMixin-sweeper' % self.__class__.__name__)
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self):
        return dict([(f.name, getattr(self, f.name)) for f in self._meta.local_fields if not f.rel])

    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])

    def dirty_fields_verbose_name(self):
        dirties = self.get_dirty_fields().keys()
        lk = []
        for k in dirties:
            vebose = self._meta.get_field_by_name(k)[0].verbose_name
            lk.append(verbose)
        return lk

    def dirty_values(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])

    def dirty_keys(self):
        return self.get_dirty_fields().keys()

    def is_dirty(self):
        if not self.pk:
            return True
        return {} != self.get_dirty_fields()


def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._as_dict()


class Log(LogEntry):

    ACTION_CHOICE = ACTION_CHOICE

    ADDITION = 1
    CHANGE = 2
    DELETION = 3
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    message_extra = models.CharField(
        max_length=400, null=True, blank=True, verbose_name=u'附加信息')

    @classmethod
    def _get_content_types(cls,app=None,model=None):
        ct = ContentType.objects.all()
        if app is None:
            ct = ct.all()
        elif isinstance(app, list):
            ct = ct.filter(app_label__in=app)
        else:
            ct = ct.filter(app_label=app)
        if model is None:
            ct = ct.all()
        elif isinstance(model, list):
            ct = ct.filter(model__in=model)
        else:
            ct = ct.filter(model=model)
        return ct

    @classmethod
    def _has_changed(cls, instance, field):
        if not instance.pk:
            return False
        old_value = instance.__class__._default_manager.\
            filter(pk=instance.pk).values(field.name).get()[field.name]
        new_value = getattr(instance, field.name)
        if new_value == old_value:
            return False
        else:
            return True

    @classmethod
    def _get_obj_fields(cls, instance):
        fields = instance._meta.fields
        return fields

    @classmethod
    def get_obj_field_verbose_name(cls, instance, field):
        return instance._meta.get_field_by_name(field.name)[0].verbose_name

    @classmethod
    def _diff_obj(cls, instance):
        l = []
        fields = cls._get_obj_fields(instance)
        for f in fields:
            if cls._has_changed(instance, f):
                l.append(cls.get_obj_field_verbose_name(instance, f))
        return ','.join(l)

    @classmethod
    def _dirty_fields(self, obj):
        pass

    @classmethod
    def set_log(cls,request,obj,action,user=None,change_message=None):
        if (request or user) is None:
            raise ValueError('you must take argument request or user')
            logging.error(ValueError('you must take argument request or user'))
        if request:
            user = request.user
        else:
            user = user
        if obj is None:
            raise TypeError('require model instance argument obj')
            logging.error(TypeError('require model instance argument obj'))
        if action is None:
            raise TypeError('require a integer argument action')
            logging.error(ValueError('require a integer argument action'))
        if change_message is None:
            msg = dict(cls.ACTION_CHOICE).get(action, '')
            if action == cls.CHANGE:
                try:
                    message_extra = ','.join(obj.get_dirty_fields().keys())
                except:
                    message_extra = ''
            else:
                message_extra = ''
        else:
            msg = change_message
            message_extra = ''
        object_repr = force_text(obj)
        return cls.objects.create(user=user,
                                  content_type=ContentType.objects.get_for_model(
                                      obj),
                                  object_id=smart_unicode(obj.pk),
                                  object_repr=smart_unicode(object_repr),
                                  change_message=smart_unicode(msg),
                                  message_extra=message_extra,
                                  action_flag=action
                                  )

    @classmethod
    def get_log(cls,user=None,model=None,app=None,action=None,obj=None,count=500):
        qs = cls.objects.all().order_by('-action_time')
        if obj is not None:
            qs = qs.objects.filter(obj=content_object,object_id=obj.pk)
        else:
            qs = qs.all()
        if user is not None:
            qs = qs.filter(user=user).all()
        else:
            qs = qs.all()
        cts = cls._get_content_types(model=model, app=app)
        qs = qs.filter(content_type__in=cts)
        if action is not None:
            qs = qs.filter(action_flag=action)
        else:
            qs = qs.all()
        return qs.all()[:count]

    def cate_name(self):
        try:
            name = self.content_object._meta.verbose_name.title()
        except Exception as e:
            name = self.content_type.name
        return name

    def get_message(self):
        username = self.user.username
        return render_to_string('common/log_msg.html',
                                 {
                                 'obj': self,
                                 'username': username,
                                 'actions': dict(Log.ACTION_CHOICE).values()
                                 })
