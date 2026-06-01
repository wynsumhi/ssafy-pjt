"""
accounts 앱 - 마이페이지 관련 views
/api/v1/mypage/
"""

from accounts.models import Follow, User
from accounts.serializers import (
    ChangePasswordSerializer,
    UserProfileSerializer,
    UserSimpleSerializer,
)
from articles.models import Article, Like
from articles.serializers import ArticleListSerializer
from django.contrib.auth.hashers import check_password
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from places.models import Place
from places.serializers import PlaceSimpleSerializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    methods=["GET"],
    tags=["mypage"],
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: UserProfileSerializer,
        401: {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": "Authentication credentials were not provided.",
                }
            },
        },
    },
)
@extend_schema(
    methods=["PATCH"],
    tags=["mypage"],
    summary="내 프로필 수정",
    description="프로필 정보를 수정합니다. (닉네임, 프로필 이미지, 소개글)",
    request=UserProfileSerializer,
    responses={
        200: UserProfileSerializer,
        400: {
            "type": "object",
            "properties": {
                "nickname": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    examples=[
        OpenApiExample(
            "Profile Update Request",
            value={
                "nickname": "새로운닉네임",
                "bio": "새로운 소개글입니다.",
                "profile_image": "https://example.com/new-profile.jpg",
            },
            request_only=True,
        ),
    ],
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """
    내 프로필 조회/수정

    GET: 내 프로필 정보 조회
    PATCH: 프로필 수정 (닉네임, 프로필 이미지, 소개글)
    """
    user = request.user

    if request.method == "GET":
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = UserProfileSerializer(
            user, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["mypage"],
    summary="비밀번호 변경",
    description="현재 비밀번호를 확인한 후 새로운 비밀번호로 변경합니다.",
    request=ChangePasswordSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "비밀번호가 변경되었습니다."}
            },
        },
        400: {
            "type": "object",
            "properties": {
                "current_password": {"type": "array", "items": {"type": "string"}},
                "new_password": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    examples=[
        OpenApiExample(
            "Change Password Request",
            value={
                "current_password": "oldpassword123!",
                "new_password": "newpassword456!",
                "new_password_confirm": "newpassword456!",
            },
            request_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    비밀번호 변경
    POST /api/v1/mypage/password/

    현재 비밀번호를 확인한 후 새 비밀번호로 변경합니다.
    """
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]

        # 현재 비밀번호 확인
        if not check_password(current_password, request.user.password):
            return Response(
                {"current_password": ["현재 비밀번호가 올바르지 않습니다."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새 비밀번호 설정
        request.user.set_password(new_password)
        request.user.save()

        return Response({"message": "비밀번호가 변경되었습니다."})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["mypage"],
    summary="좋아요한 게시글 목록",
    description="내가 좋아요한 게시글 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="페이지 번호 (기본: 1)",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="페이지당 게시글 수 (기본: 30, 최대: 100)",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "results": {"type": "array", "items": {"type": "object"}},
                "pagination": {
                    "type": "object",
                    "properties": {
                        "current_page": {"type": "integer"},
                        "total_pages": {"type": "integer"},
                        "total_count": {"type": "integer"},
                        "has_next": {"type": "boolean"},
                        "has_previous": {"type": "boolean"},
                    },
                },
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def liked_articles(request):
    """
    좋아요한 게시글 목록
    GET /api/v1/mypage/likes/

    내가 좋아요한 게시글 목록을 최신순으로 조회합니다.
    """
    # 좋아요한 게시글 가져오기
    liked_article_ids = Like.objects.filter(user=request.user).values_list(
        "article_id", flat=True
    )

    articles = (
        Article.objects.filter(id__in=liked_article_ids, is_published=True)
        .select_related("user", "place")
        .order_by("-created_at")
    )

    # 페이지네이션
    page = int(request.GET.get("page", 1))
    page_size = min(int(request.GET.get("page_size", 30)), 100)

    start = (page - 1) * page_size
    end = start + page_size

    total_count = articles.count()
    total_pages = (total_count + page_size - 1) // page_size

    paginated_articles = articles[start:end]

    serializer = ArticleListSerializer(
        paginated_articles, many=True, context={"request": request}
    )

    return Response(
        {
            "results": serializer.data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }
    )


@extend_schema(
    tags=["mypage"],
    summary="저장한 장소 목록",
    description="내가 저장한 장소 목록을 조회합니다. (최대 10개)",
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="카테고리 필터 (선택)",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "results": {"type": "array", "items": {"type": "object"}},
                "total": {"type": "integer", "description": "총 저장 개수"},
                "limit": {"type": "integer", "description": "최대 저장 가능 개수"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saved_places(request):
    """
    저장한 장소 목록
    GET /api/v1/mypage/saved-places/

    내가 저장한 장소 목록을 조회합니다. (최대 10개)
    """
    saved_cids = request.user.saved_places

    if not saved_cids:
        return Response({"results": [], "total": 0, "limit": 10})

    # 저장한 장소 가져오기
    places = Place.objects.filter(cid__in=saved_cids)

    # 카테고리 필터링
    category = request.GET.get("category")
    if category:
        places = places.filter(category_path__icontains=category)

    serializer = PlaceSimpleSerializer(places, many=True)

    return Response({"results": serializer.data, "total": len(saved_cids), "limit": 10})


@extend_schema(
    tags=["mypage"],
    summary="내 게시글 목록",
    description="내가 작성한 게시글 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="페이지 번호 (기본: 1)",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="페이지당 게시글 수 (기본: 30, 최대: 100)",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "results": {"type": "array", "items": {"type": "object"}},
                "pagination": {
                    "type": "object",
                    "properties": {
                        "current_page": {"type": "integer"},
                        "total_pages": {"type": "integer"},
                        "total_count": {"type": "integer"},
                    },
                },
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_articles(request):
    """
    내 게시글 목록
    GET /api/v1/mypage/articles/

    내가 작성한 게시글 목록을 최신순으로 조회합니다.
    """
    articles = (
        Article.objects.filter(user=request.user, is_published=True)
        .select_related("place")
        .order_by("-created_at")
    )

    # 페이지네이션
    page = int(request.GET.get("page", 1))
    page_size = min(int(request.GET.get("page_size", 30)), 100)

    start = (page - 1) * page_size
    end = start + page_size

    total_count = articles.count()
    total_pages = (total_count + page_size - 1) // page_size

    paginated_articles = articles[start:end]

    serializer = ArticleListSerializer(
        paginated_articles, many=True, context={"request": request}
    )

    return Response(
        {
            "results": serializer.data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }
    )
