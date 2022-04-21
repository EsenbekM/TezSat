import uuid

from django.db import models


# Create your models here.
class AdvertisementType(models.Model):
    """
    Grouping advertisement into different types, P.S don't change db_table, golang ad-server
     server won't understand django format of naming table
    """
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "advertisement_type"

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    """
    Model for storing advertisement, same as AdvertisementType
    """
    id = models.UUIDField(primary_key=True, editable=False)
    type = models.ForeignKey(AdvertisementType, on_delete=models.CASCADE, related_name="ads")
    link = models.URLField()
    image_link = models.ImageField(upload_to="abc/")
    click_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    def save(self, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        super(Advertisement, self).save(**kwargs)

    class Meta:
        db_table = "advertisement"


class AdvertisementStatistics(models.Model):
    """
    Model for logging each ad click and view
    """
    CLICK = 'click'
    VIEW = 'view'
    TYPE = (
        (CLICK, CLICK),
        (VIEW, VIEW)
    )
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.SET_NULL, related_name="statistics", null=True
    )
    type = models.CharField(max_length=20)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "advertisement_stats"
