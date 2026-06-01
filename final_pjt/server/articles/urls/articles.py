"""
articles 앱 - 게시글 관련 URLs
/api/v1/articles/
"""

from articles.views import articles
from django.urls import path

app_name = "articles"

urlpatterns = [
    # GET: 목록 조회, POST: 게시글 작성
    path("", articles.article_list, name="article-list"),
    # GET: 상세 조회, PATCH: 수정, DELETE: 삭제
    path("<int:article_id>/", articles.article_detail, name="article-detail"),
    # GET: 좋아요 추가, DELETE: 좋아요 취소
    path("<int:article_id>/like/", articles.article_like, name="article-like"),
]
