from django.db import models


class BoxItem(models.Model):
    box = models.ForeignKey('Box', on_delete=models.CASCADE, related_name='inventory')
    item = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['box', 'item'], name='unique box item')
        ]
