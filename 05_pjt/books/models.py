from django.db import models

# Create your models here.


class Book(models.Model):

    # 회원 리뷰 평점
    RATING_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]

    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        default=5,
        help_text="PLEASE ENTER RATING",
        verbose_name="RATING",
    )

    title = models.CharField(max_length=100, verbose_name="TITLE")
    description = models.TextField(blank=True, verbose_name="DESCRIPTION")
    author = models.CharField(max_length=50, verbose_name="AUTHOR")
    
    

