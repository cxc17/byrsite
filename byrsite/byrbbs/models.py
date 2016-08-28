from __future__ import unicode_literals

from django.db import models

# Create your models here.


class board(models.Model):
    board_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'board'
