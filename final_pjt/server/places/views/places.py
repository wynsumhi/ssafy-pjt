"""
places 앱 - 장소 관련 views
/api/v1/places/
"""

import math

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from places.models import Place
from places.serializers import (
    PlaceDetailSerializer,
    PlaceListSerializer,
    PlaceSimpleSerializer,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response


@extend_schema(
    tags=["places"],
    summary="장소 목록 조회",
    description="장소 목록을 검색하고 필터링합니다.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="검색어 (제목, 요약)",
        ),
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="카테고리 필터 (예: 카페, 음식, 관광)",
        ),
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
            description="페이지당 장소 수 (기본: 30, 최대: 100)",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "results": {"type": "array", "items": {"type": "object"}},
                "pagination": {
                    "type": "object",
                    "properties": {
                        "current_page": {"type": "integer"},
                        "total_pages": {"type": "integer"},
                        "total_count": {"type": "integer"},
                        "has_next": {"type": "boolean"},
                        "has_previous": {"type": "boolean"},
                    },
                },
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def place_list(request):
    """
    장소 목록 조회
    GET /api/v1/places/

    장소를 검색하고 필터링합니다.
    """
    places = Place.objects.all()

    # 검색
    search = request.GET.get("search")
    if search:
        places = places.filter(title__icontains=search) | places.filter(
            summary__icontains=search
        )

    # 카테고리 필터
    category = request.GET.get("category")
    if category:
        places = places.filter(category_path__icontains=category)

    # 정렬
    places = places.order_by("-created_at")

    # 페이지네이션 (게시글 작성용이므로 작은 사이즈)
    page = int(request.query_params.get("page", 1))
    page_size = min(int(request.query_params.get("page_size", 20)), 50)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    total_count = places.count()
    paginated_places = places[start_idx:end_idx]

    serializer = PlaceListSerializer(
        paginated_places, many=True, context={"request": request}
    )

    return Response(
        {
            "results": serializer.data,
            "pagination": {
                "current_page": page,
                "total_pages": math.ceil(total_count / page_size) if total_count else 0,
                "total_count": total_count,
                "has_next": end_idx < total_count,
                "has_previous": page > 1,
                "page_size": page_size,
            },
        }
    )


@extend_schema(
    tags=["places"],
    summary="장소 상세 조회",
    description="특정 장소의 상세 정보를 조회합니다.",
    responses={
        200: PlaceDetailSerializer,
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "장소를 찾을 수 없습니다"}
            },
        },
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def place_detail(request, cid):
    """
    장소 상세 조회
    GET /api/v1/places/{cid}/

    특정 장소의 상세 정보를 조회합니다.
    """
    place = get_object_or_404(Place, cid=cid)

    serializer = PlaceDetailSerializer(place)

    # 저장 여부 추가 (로그인한 경우)
    data = serializer.data
    if request.user.is_authenticated:
        data["is_saved"] = cid in request.user.saved_places
    else:
        data["is_saved"] = False

    return Response(data)


@extend_schema(
    methods=["POST"],
    tags=["places"],
    summary="장소 저장",
    description="장소를 내 저장 목록에 추가합니다. (최대 10개)",
    request=None,
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "장소를 저장했습니다"},
                "is_saved": {"type": "boolean", "example": True},
                "saved_count": {"type": "integer", "description": "총 저장 개수"},
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "저장 가능한 최대 개수(10개)를 초과했습니다",
                }
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "장소를 찾을 수 없습니다"}
            },
        },
    },
)
@extend_schema(
    methods=["DELETE"],
    tags=["places"],
    summary="장소 저장 취소",
    description="저장한 장소를 목록에서 제거합니다.",
    request=None,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "저장을 취소했습니다"},
                "is_saved": {"type": "boolean", "example": False},
                "saved_count": {"type": "integer", "description": "총 저장 개수"},
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "장소를 찾을 수 없습니다"}
            },
        },
    },
)
@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def place_save_toggle(request, cid):
    """
    장소 저장/취소

    POST: 장소 저장 (최대 10개)
    DELETE: 저장 취소
    """
    # 장소 존재 확인
    place = get_object_or_404(Place, cid=cid)

    if request.method == "POST":
        # 저장
        success, message = request.user.add_saved_place(cid)

        if not success:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": message,
                "is_saved": True,
                "saved_count": len(request.user.saved_places),
            },
            status=status.HTTP_201_CREATED,
        )

    elif request.method == "DELETE":
        # 저장 취소
        success = request.user.remove_saved_place(cid)

        if success:
            message = "저장을 취소했습니다"
        else:
            message = "저장하지 않은 장소입니다"

        return Response(
            {
                "message": message,
                "is_saved": False,
                "saved_count": len(request.user.saved_places),
            }
        )
