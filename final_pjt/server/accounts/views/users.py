"""
accounts 앱 - 사용자 관련 Views
"""

from accounts.models import Follow, User
from accounts.serializers import UserProfileSerializer, UserSimpleSerializer
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    tags=["users"],
    summary="사용자 프로필 조회",
    description="특정 사용자의 공개 프로필을 조회합니다.",
    responses={
        200: UserProfileSerializer,
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "사용자를 찾을 수 없습니다"}
            },
        },
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request, user_id):
    """
    사용자 프로필 조회
    GET /api/v1/users/{user_id}/

    다른 사용자의 공개 프로필 정보를 조회합니다.
    팔로우 여부, 게시글 수, 팔로워/팔로잉 수가 포함됩니다.
    """

    user = get_object_or_404(
        User.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_published=True)),
            follower_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
        ),
        pk=user_id,
    )

    serializer = UserProfileSerializer(user, context={"request": request})
    return Response(serializer.data)


@extend_schema(
    methods=["POST"],
    tags=["users"],
    summary="팔로우",
    description="사용자를 팔로우합니다.",
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "팔로우했습니다"},
                "is_following": {"type": "boolean", "example": True},
                "follower_count": {"type": "integer", "example": 101},
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "이미 팔로우한 사용자입니다",
                }
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "사용자를 찾을 수 없습니다"}
            },
        },
    },
)
@extend_schema(
    methods=["DELETE"],
    tags=["users"],
    summary="언팔로우",
    description="팔로우를 취소합니다.",
    responses={
        204: None,
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "팔로우하지 않은 사용자입니다"}
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "사용자를 찾을 수 없습니다"}
            },
        },
    },
)
@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """
    팔로우/언팔로우
    POST /api/v1/users/{user_id}/follow/     # 팔로우
    DELETE /api/v1/users/{user_id}/follow/   # 언팔로우

    다른 사용자를 팔로우하거나 언팔로우합니다.
    자기 자신은 팔로우할 수 없습니다.
    """

    # 팔로우 대상 사용자 확인
    following = get_object_or_404(User, pk=user_id)

    # 자기 자신 팔로우 방지
    if request.user == following:
        return Response(
            {"error": "자기 자신을 팔로우할 수 없습니다"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # 팔로워 수 계산
    follower_count = following.followers.count()

    if request.method == "POST":
        # 팔로우
        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=following
        )

        if not created:
            return Response(
                {"error": "이미 팔로우한 사용자입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "팔로우했습니다",
                "is_following": True,
                "follower_count": follower_count,
            },
            status=status.HTTP_201_CREATED,
        )

    elif request.method == "DELETE":
        # 언팔로우
        try:
            follow = Follow.objects.get(follower=request.user, following=following)
            follow.delete()
            follower_count -= 1
        except Follow.DoesNotExist:
            return Response(
                {"error": "팔로우하지 않은 사용자입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    tags=["users"],
    summary="팔로워 목록 조회",
    description="사용자의 팔로워 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="페이지 번호 (기본: 1)",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="페이지당 사용자 수 (기본: 50, 최대: 100)",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/UserSimple"},
                },
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
def followers_list(request, user_id):
    """
    팔로워 목록 조회
    GET /api/v1/users/{user_id}/followers/

    사용자를 팔로우하는 사람들의 목록을 조회합니다.
    """

    user = get_object_or_404(User, pk=user_id)

    # 팔로워 목록 (나를 팔로우하는 사람들)
    followers = (
        User.objects.filter(following__following=user).distinct().order_by("-id")
    )

    # 페이지네이션
    page = int(request.query_params.get("page", 1))
    page_size = min(int(request.query_params.get("page_size", 50)), 100)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    total_count = followers.count()
    paginated_followers = followers[start_idx:end_idx]

    serializer = UserSimpleSerializer(
        paginated_followers, many=True, context={"request": request}
    )

    return Response(
        {
            "results": serializer.data,
            "pagination": {
                "current_page": page,
                "total_pages": (total_count + page_size - 1) // page_size,
                "total_count": total_count,
                "has_next": end_idx < total_count,
                "has_previous": page > 1,
            },
        }
    )


@extend_schema(
    tags=["users"],
    summary="팔로잉 목록 조회",
    description="사용자가 팔로우하는 사람들의 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="페이지 번호 (기본: 1)",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="페이지당 사용자 수 (기본: 50, 최대: 100)",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/UserSimple"},
                },
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
def following_list(request, user_id):
    """
    팔로잉 목록 조회
    GET /api/v1/users/{user_id}/following/

    사용자가 팔로우하는 사람들의 목록을 조회합니다.
    """

    user = get_object_or_404(User, pk=user_id)

    # 팔로잉 목록 (내가 팔로우하는 사람들)
    following = User.objects.filter(followers__follower=user).distinct().order_by("-id")

    # 페이지네이션
    page = int(request.query_params.get("page", 1))
    page_size = min(int(request.query_params.get("page_size", 50)), 100)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    total_count = following.count()
    paginated_following = following[start_idx:end_idx]

    serializer = UserSimpleSerializer(
        paginated_following, many=True, context={"request": request}
    )

    return Response(
        {
            "results": serializer.data,
            "pagination": {
                "current_page": page,
                "total_pages": (total_count + page_size - 1) // page_size,
                "total_count": total_count,
                "has_next": end_idx < total_count,
                "has_previous": page > 1,
            },
        }
    )
