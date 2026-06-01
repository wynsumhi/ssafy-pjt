# articles/views/articles.py
"""
articles 앱 - 게시글 관련 views
/api/v1/articles/
"""

from accounts.models import Follow
from articles.models import Article, Like
from articles.serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
)
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    methods=["GET"],
    tags=["articles"],
    summary="게시글 목록 조회",
    description="팔로우한 사용자의 게시글 목록을 조회합니다.",
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
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="카테고리 필터 (예: 카페, 음식점)",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="검색어 (제목, 내용)",
        ),
    ],
    responses={200: ArticleListSerializer(many=True)},
)
@extend_schema(
    methods=["POST"],
    tags=["articles"],
    summary="게시글 작성",
    description="새로운 게시글을 작성합니다.",
    request=ArticleCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            "게시글 작성 예시",
            value={
                "title": "청계천 탐방후기",
                "content": "탁 트인 뷰가 인상적인 곳이에요!",
                "place_cid": "KOP000034",
                "hashtags": ["맛집", "청계천", "데이트"],
                "images": ["https://picsum.photos/1080/720?random=1"],
            },
            request_only=True,
        ),
    ],
    responses={
        201: ArticleListSerializer,
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
            },
        },
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def article_list(request):
    if request.method == "GET":
        """
        게시글 목록 조회 (팔로우 피드)
        GET /api/v1/articles/

        Query Parameters:
        - page: 페이지 번호 (기본: 1)
        - page_size: 페이지당 개수 (기본: 30, 최대: 100)
        - category: 카테고리 필터 (선택)
        - search: 검색어 (제목, 내용)
        """
        # 팔로우한 사용자의 게시글만 조회
        following_users = Follow.objects.filter(follower=request.user).values_list(
            "following_id", flat=True
        )

        articles = (
            Article.objects.filter(user_id__in=following_users, is_published=True)
            .select_related("user", "place")
            .order_by("-created_at")
        )

        # 카테고리 필터
        category = request.GET.get("category")
        if category:
            articles = articles.filter(place__category_path__icontains=category)

        # 검색어 필터
        search = request.GET.get("search")
        if search:
            articles = articles.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        # 페이지네이션
        page = request.GET.get("page", 1)
        page_size = min(int(request.GET.get("page_size", 30)), 100)

        paginator = Paginator(articles, page_size)
        page_obj = paginator.get_page(page)

        # Serializer로 변환
        serializer = ArticleListSerializer(
            page_obj.object_list, many=True, context={"request": request}
        )

        return Response(
            {
                "articles": serializer.data,
                "pagination": {
                    "current_page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_count": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                },
            }
        )

    elif request.method == "POST":
        """
        게시글 작성
        POST /api/v1/articles/

        Body (multipart/form-data):
        - title: 제목 (필수, 최대 500자)
        - content: 내용 (필수, 최대 1000자)
        - place_cid: 장소 ID (필수)
        - hashtags: 해시태그 배열 (선택, 최대 10개)
        - images: 이미지 파일들 (선택, 최대 5개)
        """
        serializer = ArticleCreateUpdateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            # user와 source는 자동 설정
            article = serializer.save(user=request.user, source="USER")

            # 응답은 ListSerializer로
            response_serializer = ArticleListSerializer(
                article, context={"request": request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=["GET"],
    tags=["articles"],
    summary="게시글 상세 조회",
    description="특정 게시글의 상세 정보를 조회합니다. 조회수가 자동으로 증가합니다.",
    responses={
        200: ArticleDetailSerializer,
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "게시글을 찾을 수 없습니다"}
            },
        },
    },
)
@extend_schema(
    methods=["PATCH"],
    tags=["articles"],
    summary="게시글 수정",
    description="작성한 게시글을 수정합니다. (장소 정보는 수정 불가)",
    request=ArticleCreateUpdateSerializer,
    responses={
        200: ArticleDetailSerializer,
        403: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "본인이 작성한 게시글만 수정할 수 있습니다",
                }
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "게시글을 찾을 수 없습니다"}
            },
        },
    },
)
@extend_schema(
    methods=["DELETE"],
    tags=["articles"],
    summary="게시글 삭제",
    description="작성한 게시글을 삭제합니다.",
    responses={
        204: None,
        403: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "본인이 작성한 게시글만 삭제할 수 있습니다",
                }
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "게시글을 찾을 수 없습니다"}
            },
        },
    },
)
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def article_detail(request, article_id):
    if request.method == "GET":
        """
        게시글 상세 조회
        GET /api/v1/articles/{article_id}/
        """
        article = get_object_or_404(
            Article.objects.select_related("user", "place"),
            pk=article_id,
            is_published=True,
        )

        # 조회수 증가
        article.view_count += 1
        article.save(update_fields=["view_count"])

        serializer = ArticleDetailSerializer(article, context={"request": request})

        return Response(serializer.data)

    elif request.method == "PATCH":
        """
        게시글 수정
        PATCH /api/v1/articles/{article_id}/

        Body (multipart/form-data):
        - title: 제목 (선택)
        - content: 내용 (선택)
        - hashtags: 해시태그 배열 (선택)
        - images: 추가 이미지 파일들 (선택)
        - delete_image_ids: 삭제할 이미지 인덱스 배열 (선택)

        Note: 장소 정보는 수정 불가
        """
        article = get_object_or_404(Article, pk=article_id)

        # 권한 확인
        if article.user != request.user:
            return Response(
                {"error": "본인이 작성한 게시글만 수정할 수 있습니다"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ArticleCreateUpdateSerializer(
            article,
            data=request.data,
            partial=True,  # PATCH이므로 부분 업데이트
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            # 응답은 DetailSerializer로
            response_serializer = ArticleDetailSerializer(
                article, context={"request": request}
            )
            return Response(response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        """
        게시글 삭제
        DELETE /api/v1/articles/{article_id}/
        """
        article = get_object_or_404(Article, pk=article_id)

        # 권한 확인
        if article.user != request.user:
            return Response(
                {"error": "본인이 작성한 게시글만 삭제할 수 있습니다"},
                status=status.HTTP_403_FORBIDDEN,
            )

        article.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    methods=["POST"],
    tags=["articles"],
    summary="좋아요 토글",
    description="게시글 좋아요를 추가하거나 취소합니다.",
    request=None,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "좋아요 했습니다"},
                "is_liked": {"type": "boolean", "example": True},
                "likes_count": {"type": "integer", "example": 16},
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "이미 좋아요한 게시글입니다"}
            },
        },
    },
)
@extend_schema(
    methods=["DELETE"],
    tags=["articles"],
    summary="좋아요 취소",
    description="게시글 좋아요를 취소합니다.",
    request=None,
    responses={
        204: None,
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "좋아요하지 않은 게시글입니다"}
            },
        },
    },
)
@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def article_like(request, article_id):
    """게시글 좋아요 추가/취소"""

    article = get_object_or_404(Article, pk=article_id, is_published=True)

    if request.method == "POST":
        # 좋아요 추가
        like, created = Like.objects.get_or_create(user=request.user, article=article)

        if not created:
            return Response(
                {"error": "이미 좋아요한 게시글입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 좋아요 수 업데이트
        article.like_count = article.likes.count()
        article.save(update_fields=["like_count"])

        return Response(
            {
                "message": "좋아요 했습니다",
                "is_liked": True,
                "likes_count": article.like_count,
            },
            status=status.HTTP_201_CREATED,
        )

    elif request.method == "DELETE":
        # 좋아요 취소
        try:
            like = Like.objects.get(user=request.user, article=article)
            like.delete()
        except Like.DoesNotExist:
            return Response(
                {"error": "좋아요하지 않은 게시글입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 좋아요 수 업데이트
        article.like_count = article.likes.count()
        article.save(update_fields=["like_count"])

        return Response(status=status.HTTP_204_NO_CONTENT)
