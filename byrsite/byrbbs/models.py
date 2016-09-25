from __future__ import unicode_literals

from django.db import models

# Create your models here.


class byr_board(models.Model):
    board_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'board'


class byr_post(models.Model):
    post_id = models.CharField(max_length=16)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=80)
    content = models.TextField(blank=True)
    user_id = models.CharField(max_length=13)
    user_name = models.CharField(max_length=40)
    board_name = models.CharField(max_length=30)
    post_num = models.IntegerField()
    publish_time = models.DateTimeField(blank=True)
    last_time = models.DateTimeField(blank=True)
    # insert_time = models.DateTimeField

    class Meta:
        db_table = 'post'


class byr_comment(models.Model):
    post_id = models.CharField(max_length=16)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=80)
    content = models.TextField(blank=True)
    user_id = models.CharField(max_length=13)
    user_name = models.CharField(max_length=40)
    publish_time = models.DateTimeField(blank=True)
    # insert_time = models.DateTimeField

    class Meta:
        db_table = 'comment'


class byr_user(models.Model):
    user_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    astro = models.CharField(max_length=255)
    qq = models.CharField(max_length=255)
    msn = models.CharField(max_length=255)

    home_page = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    post_count = models.IntegerField()
    score = models.IntegerField()
    life = models.IntegerField()
    last_login_time = models.DateTimeField(blank=True)

    last_login_ip = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    face_url = models.CharField(max_length=255)
    face_height = models.FloatField()
    face_width = models.FloatField()

    class Meta:
        db_table = 'user'


class byr_data(models.Model):
    data_name = models.CharField(max_length=255)
    data_value = models.TextField(blank=True)

    class Meta:
        db_table = 'data'

