from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Place


class PlaceListSerializer(serializers.ModelSerializer):
    """장소 목록용 (간단한 정보)"""

    class Meta:
        model = Place
        fields = [
            "cid",
            "title",
            "category_path",
            "summary",
            "main_image",
            "address_new",
            "latitude",
            "longitude",
            "tags",
        ]

        def get_distance(self, obj):
            """사용자 위치로부터의 거리 (km) - context에서 전달받음"""
            # View에서 계산된 거리를 전달받아 사용
            return getattr(obj, "distance", None)

        def get_articles_count(self, obj):
            """해당 장소의 게시글 수"""
            # prefetch_related로 최적화 가능
            if hasattr(obj, "articles_count"):
                return obj.articles_count
            return obj.articles.count()


class PlaceDetailSerializer(serializers.ModelSerializer):
    """장소 상세용 (전체 정보)"""

    is_saved = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = "__all__"

    @extend_schema_field(serializers.BooleanField)
    def get_is_saved(self, obj):
        """현재 사용자가 저장한 장소인지 확인"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.cid in request.user.saved_places
        return False

    @extend_schema_field(serializers.IntegerField)
    def get_articles_count(self, obj):
        """해당 장소의 게시글 수"""
        if hasattr(obj, "articles_count"):
            return obj.articles_count
        return obj.articles.count()


class PlaceSimpleSerializer(serializers.ModelSerializer):
    """게시글 목록 조회시에 포함되는 장소 정보 (최소)"""

    class Meta:
        model = Place
        fields = [
            "cid",
            "title",
            "main_image",
            "address_new",
            "latitude",
            "longitude",
            "category_path",
        ]
