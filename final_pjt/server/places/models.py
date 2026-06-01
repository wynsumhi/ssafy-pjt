# Create your models here.
# server/places/models.py
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class PlaceCID(models.Model):
    """Visit Seoul API 목록 조회로 수집한 CID"""

    cid = models.CharField(max_length=50, primary_key=True)
    category_sn = models.CharField(max_length=50, db_index=True)
    category_path = models.CharField(
        max_length=200,
        blank=True,
        help_text='카테고리 경로 (예: " 문화관광 > 전시시설")',
    )
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True)
    main_image = models.URLField(max_length=500, blank=True)

    # 수집 상태 관리
    is_fetched = models.BooleanField(default=False, db_index=True)
    fetch_attempted_at = models.DateTimeField(null=True, blank=True)
    fetch_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "place_cids"
        indexes = [
            models.Index(fields=["is_fetched", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.cid})"

    def get_category_list(self):
        """카테고리 경로를 리스트로 변환"""
        if not self.category_path:
            return []
        return [cat.strip() for cat in self.category_path.split(">")]


class Place(models.Model):
    """장소 상세 정보"""

    cid = models.CharField(max_length=50, primary_key=True)
    category_sn = models.CharField(max_length=50, db_index=True)
    category_path = models.CharField(
        max_length=200,
        blank=True,
        help_text='카테고리 경로 (예: " 문화관광 > 전시시설")',
    )

    # 기본 정보
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)

    # 이미지
    main_image = models.URLField(max_length=500, blank=True)
    related_images = ArrayField(models.URLField(max_length=500), default=list)

    # 위치 정보
    address = models.CharField(max_length=500, blank=True)
    address_new = models.CharField(max_length=500, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(
        max_digits=12, decimal_places=9, null=True, db_index=True
    )
    longitude = models.DecimalField(
        max_digits=12, decimal_places=9, null=True, db_index=True
    )
    subway_info = models.TextField(blank=True)

    # 운영 정보
    phone = models.CharField(max_length=50, blank=True)
    homepage = models.URLField(max_length=500, blank=True)
    opening_hours = models.TextField(blank=True)
    closed_days = models.TextField(blank=True)
    fee_info = models.TextField(blank=True)

    # 접근성
    disabled_facilities = ArrayField(models.CharField(max_length=200), default=list)

    # 태그
    tags = ArrayField(models.CharField(max_length=100), default=list, db_index=True)

    # 일정
    schedule_start = models.DateField(null=True, blank=True)
    schedule_end = models.DateField(null=True, blank=True)

    # 원본 데이터
    raw_data = models.JSONField(default=dict, blank=True)

    # AI 추천용 임베딩
    embedding_vector = ArrayField(models.FloatField(), size=128, null=True, blank=True)

    # 메타 정보
    created_at_api = models.DateField(null=True)
    updated_at_api = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "places"
        indexes = [
            models.Index(fields=["category_sn", "latitude", "longitude"]),
            models.Index(fields=["tags"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.cid})"

    def get_category_list(self):
        """카테고리 경로를 리스트로 변환"""
        if not self.category_path:
            return []
        return [cat.strip() for cat in self.category_path.split(">")]
