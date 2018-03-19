from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone

# Create your models here.
class Contents(models.Model):
    mention_index = models.CharField(max_length=5, default='0')  # 멘션 index
    mention_order = models.CharField(max_length=5, default='0')  # 멘션 순서
    username = models.CharField(max_length=30)                   # 유저 아이디
    contents = models.CharField(max_length=150)                  # 장작 내용
    image = models.FileField(null=True)                          # 그림
    created_date = models.CharField(max_length=14)               # 작성일
    deleted = models.IntegerField(default=0)                     # 삭제여부

    def __str__(self):
        return self.contents