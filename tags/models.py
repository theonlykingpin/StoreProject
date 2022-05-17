from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class TaggedItemManager(models.Manager):

    def get_tags_for(self, obj_type, obj_id):
        content_type = ContentType.objects.get_for_model(obj_type)
        return TaggedItem.objects.select_related('tag').filter(content_type=content_type, object_id=obj_id)


class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['label']


class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = TaggedItemManager()

    def __str__(self):
        return self.tag.label

    class Meta:
        verbose_name = 'Tagged Item'
        verbose_name_plural = 'Tagged Items'
        ordering = ['tag']
