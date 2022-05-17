from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class LikedItem(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = 'Liked Item'
        verbose_name_plural = 'Liked Items'
        ordering = ['-user__date_joined']
