# articles/urls/comments.py
"""
articles 앱 - 댓글 관련 URLs
/api/v1/comments/
"""

from articles.views import comments
from django.urls import path

app_name = "comments"

urlpatterns = [
    # GET: 목록, POST: 생성
    path("", comments.comment_list, name="comment-list"),
    # GET: 조회, PATCH: 수정, DELETE: 삭제
    path("<int:comment_id>/", comments.comment_detail, name="comment-detail"),
]
