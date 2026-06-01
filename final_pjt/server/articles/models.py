# server/articles/models.py
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Article(models.Model):
    """게시글 (AI 생성 + 사용자 작성)"""

    SOURCE_CHOICES = [
        ("AI", "AI 생성"),
        ("USER", "사용자 작성"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    place = models.ForeignKey(
        "places.Place", on_delete=models.CASCADE, related_name="articles"
    )

    # 게시글 내용
    title = models.CharField(max_length=500)
    content = models.TextField()
    images = ArrayField(models.URLField(max_length=500), default=list)
    tags = ArrayField(models.CharField(max_length=100), default=list)

    # 출처
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="USER")

    # AI 생성 메타데이터 (source='AI'인 경우만 사용)
    generation_metadata = models.JSONField(default=dict, blank=True)

    # 임베딩
    embedding_vector = ArrayField(models.FloatField(), size=128, null=True, blank=True)

    # 통계
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    save_count = models.IntegerField(default=0)

    # 관리
    is_published = models.BooleanField(default=True)
    quality_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "articles"
        indexes = [
            models.Index(fields=["place", "is_published"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["source", "is_published"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.source})"


class Comment(models.Model):
    """
    게시글 댓글 모델
    - 익명 표시 (항상 익명)
    - 1게시글 1댓글 원칙
    """

    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="게시글",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments",
        verbose_name="작성자",
    )

    content = models.TextField(max_length=300, verbose_name="댓글 내용")

    is_anonymous = models.BooleanField(default=True, verbose_name="익명 여부")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = "comments"
        verbose_name = "댓글"
        verbose_name_plural = "댓글"
        ordering = ["created_at"]

        # 1게시글 1댓글 제약 조건
        constraints = [
            models.UniqueConstraint(
                fields=["article", "user"], name="unique_comment_per_user_article"
            )
        ]

        indexes = [
            models.Index(fields=["article", "created_at"]),
        ]

    def __str__(self):
        return f"익명 - {self.article.title[:20]}"


class Like(models.Model):
    """
    게시글 좋아요 모델
    - 사용자당 게시글 1개만 좋아요 가능
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="사용자",
    )

    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="게시글",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="좋아요 일시")

    class Meta:
        db_table = "likes"
        verbose_name = "좋아요"
        verbose_name_plural = "좋아요"
        ordering = ["-created_at"]

        # 중복 좋아요 방지
        constraints = [
            models.UniqueConstraint(
                fields=["user", "article"], name="unique_like_per_user_article"
            )
        ]

        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["article"]),
        ]

    def __str__(self):
        return f"{self.user.nickname} - {self.article.title[:20]}"
