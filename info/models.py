from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_version(version):
    nums = version.split('.')
    if len(nums) != 3:
        raise ValidationError(_('invalid format, 3 numbers separated by a dot are required. Example: 1.0.0'))
    for num in nums:
        try:
            int(num)
        except ValueError:
            raise ValidationError(_('invalid format, 3 numbers separated by a dot are required. Example: 1.0.0'))
    return version


class Info(models.Model):
    class Meta:
        db_table = 'info'

    app_version = models.CharField(_('app version'), null=False, default='1.0.0', validators=(validate_version,),
                                   max_length=20)

    def save(self, *args, **kwargs):
        count = Info.objects.all().count()
        save_permission = Info.has_add_permission(self)
        if count < 1:
            super(Info, self).save()
        elif save_permission:
            super(Info, self).save()

    def has_add_permission(self):
        return Info.objects.filter(id=self.id).exists()
