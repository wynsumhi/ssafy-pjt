"""
accounts 앱 - 사용자 관련 URLs
/api/v1/users/
"""

from accounts.views import users
from django.urls import path

app_name = "users"

urlpatterns = [
    # GET: 사용자 조회하기
    path("<int:user_id>/", users.user_profile, name="user-profile"),
    # POST: 사용자 팔로우하기, DELETE: 사용자 팔로우 취소
    path("<int:user_id>/follow/", users.follow_user, name="follow"),
    # GET: 팔로워 목록 조회
    path("<int:user_id>/followers/", users.followers_list, name="followers-list"),
    # GET: 팔로잉 목록 조회
    path("<int:user_id>/following/", users.following_list, name="following-list"),
]
