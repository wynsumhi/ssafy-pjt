from accounts.serializers import LoginSerializer, SignupSerializer, UserSimpleSerializer
from django.contrib.auth import authenticate
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


@extend_schema(
    tags=["auth"],
    summary="회원가입",
    description="새로운 사용자 계정을 생성하고 JWT 토큰을 발급합니다.",
    request=SignupSerializer,
    responses={
        201: {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nickname": {"type": "string"},
                        "profile_image": {"type": "string", "nullable": True},
                    },
                },
                "message": {"type": "string", "example": "회원가입이 완료되었습니다."},
                "token": {
                    "type": "object",
                    "properties": {
                        "access": {
                            "type": "string",
                            "description": "Access Token (1시간)",
                        },
                        "refresh": {
                            "type": "string",
                            "description": "Refresh Token (7일)",
                        },
                    },
                },
            },
        },
        400: {
            "type": "object",
            "properties": {
                "username": {"type": "array", "items": {"type": "string"}},
                "password": {"type": "array", "items": {"type": "string"}},
                "nickname": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    examples=[
        OpenApiExample(
            "Signup Request",
            value={
                "username": "user123",
                "password": "password123!",
                "password2": "password123!",
                "nickname": "지구깡유저",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Signup Success",
            value={
                "user": {"id": 1, "nickname": "지구깡유저", "profile_image": None},
                "message": "회원가입이 완료되었습니다.",
                "token": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                },
            },
            response_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    회원가입 API
    POST /api/v1/auth/signup/
    """
    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSimpleSerializer(user).data,
                "message": "회원가입이 완료되었습니다.",
                "token": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["auth"],
    summary="로그인",
    description="사용자 인증 후 JWT 토큰을 발급합니다.",
    request=LoginSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nickname": {"type": "string"},
                        "profile_image": {"type": "string", "nullable": True},
                    },
                },
                "message": {"type": "string", "example": "로그인 성공"},
                "token": {
                    "type": "object",
                    "properties": {
                        "access": {
                            "type": "string",
                            "description": "Access Token (1시간)",
                        },
                        "refresh": {
                            "type": "string",
                            "description": "Refresh Token (7일)",
                        },
                    },
                },
            },
        },
        401: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "아이디 또는 비밀번호가 올바르지 않습니다.",
                }
            },
        },
        400: {
            "type": "object",
            "properties": {
                "username": {"type": "array", "items": {"type": "string"}},
                "password": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    examples=[
        OpenApiExample(
            "Login Request",
            value={"username": "user1", "password": "password123!"},
            request_only=True,
        ),
        OpenApiExample(
            "Login Success",
            value={
                "user": {
                    "id": 1,
                    "nickname": "지구깡유저",
                    "profile_image": "https://example.com/profile/1.jpg",
                },
                "message": "로그인 성공",
                "token": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                },
            },
            response_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    로그인 API
    POST /api/v1/auth/login/
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": UserSimpleSerializer(user).data,
                    "message": "로그인 성공",
                    "token": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "아이디 또는 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["auth"],
    summary="로그아웃",
    description="Refresh Token을 블랙리스트에 추가하여 무효화합니다.",
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
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "로그아웃되었습니다."}
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "로그아웃 처리 중 오류가 발생했습니다.",
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            "Logout Request",
            value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."},
            request_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    로그아웃 API
    POST /api/v1/auth/logout/

    Refresh Token을 블랙리스트에 추가하여 무효화
    """
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({"message": "로그아웃되었습니다."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": "로그아웃 처리 중 오류가 발생했습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    tags=["auth"],
    summary="현재 사용자 정보 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다.",
    responses={
        200: UserSimpleSerializer,
        401: {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": "Authentication credentials were not provided.",
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            "User Info Success",
            value={
                "id": 1,
                "nickname": "지구깡유저",
                "profile_image": "https://example.com/profile/1.jpg",
            },
            response_only=True,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """
    현재 로그인한 사용자 정보 조회
    GET /api/v1/auth/user/
    """
    serializer = UserSimpleSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
