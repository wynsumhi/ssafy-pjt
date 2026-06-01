# articles/serializers.py
from accounts.serializers import UserSimpleSerializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from places.models import Place
from places.serializers import PlaceSimpleSerializer
from rest_framework import serializers

from .models import Article, Comment, Like


class CommentSerializer(serializers.ModelSerializer):
    """댓글 Serializer"""

    author_display = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "author_display",
            "is_mine",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    @extend_schema_field(serializers.CharField)
    def get_author_display(self, obj):
        """익명 표시 (익명1, 익명2...)"""
        # 게시글 기준으로 댓글 순서를 구해서 익명 번호 부여
        article_comments = Comment.objects.filter(article=obj.article).order_by(
            "created_at"
        )

        for idx, comment in enumerate(article_comments, start=1):
            if comment.id == obj.id:
                return f"익명{idx}"
        return "익명"

    @extend_schema_field(serializers.BooleanField)
    def get_is_mine(self, obj):
        """내가 작성한 댓글인지 확인"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.user_id == request.user.id
        return False


class ArticleListSerializer(serializers.ModelSerializer):
    """게시글 목록용 Serializer (간략한 정보)"""

    author = UserSimpleSerializer(read_only=True)
    place = PlaceSimpleSerializer(read_only=True)
    thumbnail = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "author",
            "place",
            "thumbnail",
            "summary",
            "source",
            "like_count",
            "comment_count",
            "is_liked",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    @extend_schema_field(serializers.CharField)
    def get_summary(self, obj):
        """장소 요약 정보 반환"""
        if obj.place.summary:
            return obj.place.summary
        return None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_thumbnail(self, obj):
        """장소의 마지막 이미지를 썸네일로 사용"""
        if obj.place.related_images and len(obj.place.related_images) > 0:
            return obj.place.related_images[-1]
        return None

    @extend_schema_field(serializers.BooleanField)
    def get_is_liked(self, obj):
        """현재 사용자가 좋아요 했는지 확인"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, article=obj).exists()
        return False


class ArticleDetailSerializer(serializers.ModelSerializer):
    """게시글 상세용 Serializer (전체 정보)"""

    class PlaceArticleSerializer(serializers.ModelSerializer):
        """게시글 출력시 사용할 장소 Serializer (summary와 image_url을 포함)"""

        class Meta:
            model = Place
            fields = [
                "cid",
                "title",
                "address_new",
                "latitude",
                "longitude",
                "category_path",
                "related_images",
                "summary",
            ]

    author = UserSimpleSerializer(read_only=True, source="user")
    place = PlaceArticleSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "place",
            "images",
            "tags",
            "source",
            "generation_metadata",
            "like_count",
            "comment_count",
            "view_count",
            "is_liked",
            "is_following",
            "is_saved",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "source",
            "generation_metadata",
            "like_count",
            "comment_count",
            "view_count",
            "is_liked",
            "is_following",
            "is_saved",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.BooleanField)
    def get_is_liked(self, obj):
        """현재 사용자가 좋아요 했는지 확인"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, article=obj).exists()
        return False

    @extend_schema_field(serializers.BooleanField)
    def get_is_saved(self, obj):
        """현재 사용자가 장소를 저장했는지 확인"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # 장소가 없으면 False
            if not getattr(obj, "place", None):
                return False
            # `saved_places` may be a list of cids or a related manager depending on implementation
            try:
                return obj.place.cid in request.user.saved_places
            except Exception:
                try:
                    return request.user.saved_places.filter(cid=obj.place.cid).exists()
                except Exception:
                    return False
        return False

    @extend_schema_field(serializers.BooleanField)
    def get_is_following(self, obj):
        """현재 사용자가 작성자(유저)를 팔로우 중인지 확인"""
        request = self.context.get("request")
        if request and request.user.is_authenticated and obj.user is not None:
            from accounts.models import Follow

            return Follow.objects.filter(
                follower=request.user, following=obj.user
            ).exists()
        return False

    @extend_schema_field(CommentSerializer(many=True))
    def get_comments(self, obj):
        """익명 처리된 댓글 목록"""
        comments = obj.comments.all().order_by("created_at")
        return CommentSerializer(comments, many=True, context=self.context).data


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """게시글 작성/수정용 Serializer"""

    place_cid = serializers.CharField(write_only=True, required=False)
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, allow_empty=True
    )
    delete_image_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "place_cid",
            "hashtags",
            "images",
            "delete_image_ids",
        ]

    def validate_title(self, value):
        """제목 검증"""
        if not value or not value.strip():
            raise serializers.ValidationError("제목은 필수입니다")
        if len(value) > 500:
            raise serializers.ValidationError("제목은 500자를 초과할 수 없습니다")
        return value.strip()

    def validate_content(self, value):
        """내용 검증"""
        if not value or not value.strip():
            raise serializers.ValidationError("내용은 필수입니다")
        if len(value) > 1000:
            raise serializers.ValidationError("내용은 1000자를 초과할 수 없습니다")
        return value.strip()

    def validate_hashtags(self, value):
        """해시태그 검증"""
        if len(value) > 10:
            raise serializers.ValidationError(
                "해시태그는 최대 10개까지 추가 가능합니다"
            )
        return value

    def validate_images(self, value):
        """이미지 검증"""
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지 업로드 가능합니다")
        return value

    def validate_place_cid(self, value):
        """장소 존재 확인"""
        from places.models import Place

        if not Place.objects.filter(cid=value).exists():
            raise serializers.ValidationError("존재하지 않는 장소입니다")
        return value

    def create(self, validated_data):
        """게시글 생성"""
        from places.models import Place

        place_cid = validated_data.pop("place_cid")
        hashtags = validated_data.pop("hashtags", [])
        validated_data.pop("delete_image_ids", None)  # create에서는 무시

        place = Place.objects.get(pk=place_cid)

        article = Article.objects.create(
            place=place, tags=hashtags, is_published=True, **validated_data
        )

        return article

    def update(self, instance, validated_data):
        """게시글 수정"""
        hashtags = validated_data.pop("hashtags", None)
        delete_image_ids = validated_data.pop("delete_image_ids", [])
        validated_data.pop("place_cid", None)  # 장소는 수정 불가

        # 이미지 삭제 처리
        if delete_image_ids and instance.images:
            instance.images = [
                img
                for i, img in enumerate(instance.images)
                if i not in delete_image_ids
            ]

        # 해시태그 업데이트
        if hashtags is not None:
            instance.tags = hashtags

        # 나머지 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CommentCreateSerializer(serializers.ModelSerializer):
    """댓글 작성/수정용 Serializer"""

    class Meta:
        model = Comment
        fields = ["content"]

    def validate_content(self, value):
        """댓글 내용 검증"""
        if not value or not value.strip():
            raise serializers.ValidationError("댓글 내용은 필수입니다")
        if len(value) > 300:
            raise serializers.ValidationError("댓글은 300자를 초과할 수 없습니다")
        return value.strip()


class LikeSerializer(serializers.ModelSerializer):
    """좋아요 Serializer"""

    class Meta:
        model = Like
        fields = ["id", "user", "article", "created_at"]
        read_only_fields = ["id", "created_at"]
        read_only_fields = ["id", "created_at"]
