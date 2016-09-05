from __future__ import unicode_literals

from django.db import models

# Create your models here.


class byr_board(models.Model):
    board_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'board'


class byr_post(models.Model):
    post_id = models.CharField(max_length=16)
    post_title = models.CharField(max_length=255)
    post_url = models.CharField(max_length=255)
    post_content = models.TextField(blank=True)
    author_id = models.CharField(max_length=255)
    author_name = models.CharField(max_length=255)
    board_name = models.CharField(max_length=255)
    post_num = models.IntegerField
    post_time = models.DateTimeField(blank=True)
    last_time = models.DateTimeField(blank=True)
    # insert_time = models.DateTimeField

    class Meta:
        db_table = 'post'


class byr_comment(models.Model):
    post_id = models.CharField(max_length=16)
    comment_url = models.CharField(max_length=255)
    comment_content = models.TextField(blank=True)
    commenter_id = models.CharField(max_length=255)
    commenter_name = models.CharField(max_length=255)
    comment_time = models.DateTimeField(blank=True)
    # insert_time = models.DateTimeField

    class Meta:
        db_table = 'comment'
