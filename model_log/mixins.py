# -*- coding: utf-8 -*-
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
            verbose = self._meta.get_field_by_name(k)[0].verbose_name
            lk.append(verbose)
        return lk

    def dirty_values(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])

    def dirty_keys(self):
        return self.get_dirty_fields().keys()

    def use_dirty(self):
        try:
            keys = self.get_dirty_fields().keys()
        except:
            keys = None
        if keys is None:
            return False
        return True

    def is_dirty(self):
        if not self.pk:
            return True
        return {} != self.get_dirty_fields()


def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._as_dict()
