from django.db import models


class Media(models.Model):  # 作品
    name = models.CharField(max_length=255, unique=True)  # 名稱
    name_original = models.CharField(max_length=255, blank=True, null=True)  # 原始名稱(日文、英文...)
    release_date = models.DateField(blank=True, null=True)  # 上映發表日期
    country = models.CharField(max_length=255, blank=True, null=True)  # 國家
    url = models.CharField(max_length=512, blank=True, null=True)  # 網址

    class Meta:
        verbose_name = '作品'

    def __str__(self):
        return self.name


class Character(models.Model):  # 角色
    media = models.ForeignKey(Media, on_delete=models.CASCADE)  # 作品連結
    name = models.CharField(max_length=255, unique=True)  # 名稱
    name_original = models.CharField(max_length=255, blank=True, null=True)  # 原始名稱(日文、英文...)
    birthday_date = models.DateField(blank=True, null=True)  # 生日
    birthday_note = models.CharField(max_length=128, blank=True, null=True)  # 生日備註
    gender = models.CharField(max_length=128, blank=True, null=True)  # 性別
    url = models.CharField(max_length=512, blank=True, null=True)  # 網址

    class Meta:
        verbose_name = '角色'

    def __str__(self):
        return self.name


class Update(models.Model):  # 更新紀錄
    type = models.CharField(max_length=255)  # 類別
    date = models.DateTimeField()  # 日期時間
    text = models.CharField(max_length=255)  # 說明
    media = models.ForeignKey(Media, on_delete=models.CASCADE, blank=True, null=True)  # 作品連結
    character = models.CharField(max_length=255, blank=True, null=True)  # 角色文字

    class Meta:
        verbose_name = '更新紀錄'

    def __str__(self):
        return self.type
