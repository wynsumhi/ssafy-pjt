"""
accounts 앱 - 마이페이지 관련 URLs
/api/v1/mypage/
"""

from accounts.views import mypage
from django.urls import path

app_name = "mypage"

urlpatterns = [
    # 프로필
    path("profile/", mypage.my_profile, name="my_profile"),
    path("password/", mypage.change_password, name="change_password"),
    # 좋아요/저장/게시글
    path("likes/", mypage.liked_articles, name="liked_articles"),
    path("saved-places/", mypage.saved_places, name="saved_places"),
    path("articles/", mypage.my_articles, name="my_articles"),
]
