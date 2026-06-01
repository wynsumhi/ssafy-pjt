"""
accounts 앱 - 인증 관련 URLs
/api/v1/auth/
"""

from accounts.views import auth
from django.urls import path
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "auth"


# 문서화된 TokenRefreshView 생성
DocumentedTokenRefreshView = extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        summary="토큰 갱신",
        description="Refresh 토큰으로 새로운 Access 토큰을 발급받습니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "Refresh Token"}
                },
                "required": ["refresh"],
            }
        },
        responses={
            200: {"type": "object", "properties": {"access": {"type": "string"}}},
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                    "code": {"type": "string"},
                },
            },
        },
        examples=[
            OpenApiExample(
                "Request",
                value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."},
                request_only=True,
            ),
            OpenApiExample(
                "Success",
                value={"access": "eyJ0eXAiOiJKV1QiLCJhbGc..."},
                response_only=True,
            ),
        ],
    )
)(TokenRefreshView)

urlpatterns = [
    # 회원가입/로그인
    path("signup/", auth.signup, name="signup"),
    path("login/", auth.login, name="login"),
    path("logout/", auth.logout, name="logout"),
    path("user/", auth.user_info, name="user_info"),
    # 토큰 관리
    path(
        "token/refresh/",
        DocumentedTokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
