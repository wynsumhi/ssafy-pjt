from django.db import models
from django.conf import settings

# Create your models here.


# F01
class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="CATEGORY")


class Book(models.Model):
    category = models.ForeignKey(Category, models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="TITLE")
    description = models.TextField(blank=True, verbose_name="DESCRIPTION")
    isbn = models.TextField(max_length=10, verbose_name="ISBN")
    cover = models.ImageField(upload_to="image/", blank=True, verbose_name="IMAGE")
    publisher = models.TextField(max_length=50, verbose_name="PUBLISHER")
    pub_date = models.DateField()
    author = models.CharField(max_length=50, verbose_name="AUTHOR")

    # 회원 리뷰 평점
    # RANK_CHOICES = [
    #     (1, "1"),
    #     (2, "2"),
    #     (3, "3"),
    #     (4, "4"),
    #     (5, "5"),
    # ]

    customer_review_rank = models.PositiveIntegerField(
        # choices=RANK_CHOICES,
        # default=5,
        # help_text="PLEASE ENTER RANK",
        verbose_name="RANK",
    )

    


class Thread(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='thread')
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=1000)
    reading_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
