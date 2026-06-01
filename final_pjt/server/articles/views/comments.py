# articles/views/comments.py
"""
articles 앱 - 댓글 관련 views
/api/v1/comments/
"""

from articles.models import Article, Comment
from articles.serializers import CommentCreateSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    methods=["GET"],
    tags=["comments"],
    summary="댓글 목록 조회",
    description="특정 게시글의 댓글 목록을 조회합니다.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "comments": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/Comment"},
                },
                "total": {"type": "integer", "description": "총 댓글 수"},
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
    methods=["POST"],
    tags=["comments"],
    summary="댓글 작성",
    description="게시글에 댓글을 작성합니다. (1게시글 1댓글 원칙)",
    request=CommentCreateSerializer,
    responses={
        201: CommentSerializer,
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "이미 이 게시글에 댓글을 작성하셨습니다",
                },
                "existing_comment_id": {"type": "integer", "example": 2},
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
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def comment_list(request, article_id):
    if request.method == "GET":
        """
        게시글의 댓글 목록 조회
        GET /api/v1/articles/{article_id}/comments/
        """
        article = get_object_or_404(Article, pk=article_id, is_published=True)

        comments = Comment.objects.filter(article=article).order_by("created_at")

        serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )

        return Response({"comments": serializer.data, "total": comments.count()})

    elif request.method == "POST":
        """
        댓글 작성
        POST /api/v1/articles/{article_id}/comments/

        Body:
        - content: 댓글 내용 (필수, 최대 300자)

        Note:
        - 1게시글 1댓글 원칙
        - 항상 익명으로 표시
        """
        article = get_object_or_404(Article, pk=article_id, is_published=True)

        # 1게시글 1댓글 체크
        existing_comment = Comment.objects.filter(
            article=article, user=request.user
        ).first()

        if existing_comment:
            return Response(
                {
                    "error": "이미 이 게시글에 댓글을 작성했습니다",
                    "existing_comment_id": existing_comment.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CommentCreateSerializer(
            data=request.data, context={"request": request, "article": article}
        )

        if serializer.is_valid():
            comment = serializer.save(
                user=request.user, article=article, is_anonymous=True  # 항상 익명
            )

            # 게시글의 댓글 수 업데이트
            article.comment_count = article.comments.count()
            article.save(update_fields=["comment_count"])

            # 응답용 Serializer (익명 번호 포함)
            response_serializer = CommentSerializer(
                comment, context={"request": request}
            )

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=["PATCH"],
    tags=["comments"],
    summary="댓글 수정",
    description="작성한 댓글을 수정합니다. (본인만 가능)",
    request=CommentCreateSerializer,
    responses={
        200: CommentSerializer,
        403: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "본인이 작성한 댓글만 수정할 수 있습니다",
                }
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "댓글을 찾을 수 없습니다"}
            },
        },
    },
)
@extend_schema(
    methods=["DELETE"],
    tags=["comments"],
    summary="댓글 삭제",
    description="작성한 댓글을 삭제합니다. (본인만 가능)",
    responses={
        204: None,
        403: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "본인이 작성한 댓글만 삭제할 수 있습니다",
                }
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "댓글을 찾을 수 없습니다"}
            },
        },
    },
)
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def comment_detail(request, article_id, comment_id):

    if request.method == "PATCH":
        """
        댓글 수정
        PATCH /api/v1/articles/{article_id}/comments/{comment_id}/

        Body:
        - content: 댓글 내용 (필수, 최대 300자)
        """
        comment = get_object_or_404(Comment, pk=comment_id)

        # 권한 확인
        if comment.user != request.user:
            return Response(
                {"error": "본인이 작성한 댓글만 수정할 수 있습니다"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CommentCreateSerializer(
            comment, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            # 응답용 Serializer (익명 번호 포함)
            response_serializer = CommentSerializer(
                comment, context={"request": request}
            )

            return Response(response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        """
        댓글 삭제
        DELETE /api/v1/articles/{article_id}/comments/{comment_id}/delete/
        """
        comment = get_object_or_404(Comment, pk=comment_id)

        # 권한 확인
        if comment.user != request.user:
            return Response(
                {"error": "본인이 작성한 댓글만 삭제할 수 있습니다"},
                status=status.HTTP_403_FORBIDDEN,
            )

        article = comment.article
        comment.delete()

        # 게시글의 댓글 수 업데이트
        article.comment_count = article.comments.count()
        article.save(update_fields=["comment_count"])

        return Response(status=status.HTTP_204_NO_CONTENT)
