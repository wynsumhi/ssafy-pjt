from accounts.models import Follow
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    """다른 Serializer에서 사용되는 간단한 사용자 정보"""

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "profile_image",
        ]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 Serializer (마이페이지용)"""

    article_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "profile_image",
            "bio",
            "article_count",
            "follower_count",
            "following_count",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "article_count",
            "follower_count",
            "following_count",
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_article_count(self, obj):
        """작성한 게시글 수"""
        return obj.articles.filter(is_published=True).count()

    @extend_schema_field(serializers.IntegerField)
    def get_follower_count(self, obj):
        """팔로워 수"""
        return obj.followers.count()

    @extend_schema_field(serializers.IntegerField)
    def get_following_count(self, obj):
        """팔로잉 수"""
        return obj.following.count()

    def validate_nickname(self, value):
        """닉네임 중복 검사 (자기 자신 제외)"""
        request = self.context.get("request")
        if request and request.user:
            if User.objects.filter(nickname=value).exclude(pk=request.user.pk).exists():
                raise serializers.ValidationError("이미 사용 중인 닉네임입니다")
        return value


class DrawHistorySerializer(serializers.Serializer):
    """뽑기 기록용 Serializer"""

    id = serializers.IntegerField()
    article = serializers.SerializerMethodField()
    place = serializers.SerializerMethodField()
    drawn_at = serializers.DateTimeField()

    def get_article(self, obj):
        """게시글 정보"""
        from articles.models import Article

        try:
            article = Article.objects.get(id=obj.get("article_id"))
            return {
                "id": article.id,
                "title": article.title,
                "thumbnail": article.images[0] if article.images else None,
                "category": article.place.category_path if article.place else None,
            }
        except Article.DoesNotExist:
            return None

    def get_place(self, obj):
        """장소 정보"""
        from places.models import Place

        try:
            place = Place.objects.get(cid=obj.get("cid"))
            return {
                "id": place.cid,
                "name": place.title,
                "address": place.address_new or place.address,
            }
        except Place.DoesNotExist:
            return None


class SavedPlaceSerializer(serializers.Serializer):
    """저장한 장소 목록용 Serializer"""

    id = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField()
    category = serializers.CharField()
    thumbnail = serializers.CharField(allow_null=True)
    articles_count = serializers.IntegerField()
    saved_at = serializers.DateTimeField()


class SignupSerializer(serializers.ModelSerializer):
    """회원가입용 Serializer"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("username", "email", "nickname", "password", "password2")
        extra_kwargs = {"email": {"required": True}, "nickname": {"required": True}}

    def validate(self, attrs):
        """비밀번호 확인 검증"""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )
        return attrs

    def validate_email(self, value):
        """이메일 중복 검사"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_nickname(self, value):
        """닉네임 중복 검사"""
        if value and User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def create(self, validated_data):
        """사용자 생성"""
        validated_data.pop("password2")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        # nickname 입력값을 받아서 변수로 저장
        nickname = validated_data.pop("nickname", None)

        # User 모델이 nickname이 필수값이 아니라서
        # 정보가 있는 경우에만 DB에 저장
        if nickname:
            user.nickname = nickname
            user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """로그인용 Serializer"""

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )


class ChangePasswordSerializer(serializers.Serializer):
    """비밀번호 변경 Serializer"""

    current_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate(self, data):
        """새 비밀번호 확인"""
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "비밀번호가 일치하지 않습니다"}
            )
        return data
