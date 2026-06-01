"""
articles 앱 - 게시글 뽑기 관련 URLs (RESTful)
/api/v1/draws/
"""

from articles.views import draw
from django.urls import path

app_name = "draws"

urlpatterns = [
    # GET: 기록 목록, POST: 뽑기 실행
    path("", draw.draw_list_or_create, name="draw-list-create"),
    # GET: 기록 상세, DELETE: 기록 삭제
    path("<int:draw_id>/", draw.draw_detail_or_destroy, name="draw-detail-destroy"),
]
