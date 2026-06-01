"""
places 앱 - 장소 관련 URLs
/api/v1/places/
"""

from django.urls import path
from places.views import places

app_name = "places"

urlpatterns = [
    # GET: 장소 목록 조회 (게시글 작성 시 장소 선택용)
    path("", places.place_list, name="place-list"),
    # GET: 장소 상세 조회
    path("<str:cid>/", places.place_detail, name="place-detail"),
    # POST: 장소 저장, DELETE: 저장한 장소 삭제
    path("<str:cid>/save/", places.place_save_toggle, name="place-save-toggle"),
]
