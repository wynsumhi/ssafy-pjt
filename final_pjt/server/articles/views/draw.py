# server/articles/views/draw.py

"""
articles 앱 - 게시글 뽑기 관련 views
/api/v1/draws/
"""

import math
import random

from articles.models import Article
from articles.serializers import ArticleDetailSerializer
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from places.models import Place
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Haversine 공식을 사용한 두 지점 간 거리 계산 (km)
    """
    R = 6371  # 지구 반경 (km)

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def get_ai_recommended_article(user, articles):
    """
    AI 기반 게시글 추천

    사용자의 좋아요 기록을 기반으로 선호도 벡터를 계산하고,
    코사인 유사도를 통해 가장 적합한 게시글을 추천합니다.

    Args:
        user: 현재 사용자
        articles: 후보 게시글 리스트

    Returns:
        선택된 게시글 (Article 인스턴스)
    """
    import logging

    import numpy as np

    logger = logging.getLogger(__name__)

    # 1. 사용자 선호도 벡터 계산 (좋아요한 게시글 기반)
    liked_articles = (
        Article.objects.filter(likes__user=user, embedding_vector__isnull=False)
        .exclude(embedding_vector=[])
        .order_by("-likes__created_at")[:20]
    )  # 최근 20개

    # 좋아요가 3개 미만이면 랜덤으로 폴백
    if liked_articles.count() < 3:
        logger.info(f"User {user.id}: 좋아요 데이터 부족, 랜덤 선택")
        return random.choice(articles)

    # 임베딩 벡터 수집
    embeddings = []
    for article in liked_articles:
        try:
            # JSON 문자열인 경우 파싱
            if isinstance(article.embedding_vector, str):
                import json

                embedding_data = json.loads(article.embedding_vector)
            else:
                embedding_data = article.embedding_vector

            embedding = np.array(embedding_data, dtype=np.float32)
            if embedding.size > 0:
                embeddings.append(embedding)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.warning(f"임베딩 파싱 실패 (article {article.id}): {e}")
            continue

    if len(embeddings) < 3:
        logger.info(f"User {user.id}: 유효한 임베딩 부족, 랜덤 선택")
        return random.choice(articles)

    # 가중 평균 계산 (최근 것에 더 높은 가중치)
    weights = np.linspace(0.5, 1.0, len(embeddings))
    user_preference = np.average(embeddings, axis=0, weights=weights)

    # 2. 후보 게시글들과 유사도 계산
    similarities = []
    for article in articles:
        try:
            # 임베딩 벡터 파싱
            if isinstance(article.embedding_vector, str):
                import json

                embedding_data = json.loads(article.embedding_vector)
            else:
                embedding_data = article.embedding_vector

            article_vector = np.array(embedding_data, dtype=np.float32)

            # 코사인 유사도 계산
            dot_product = np.dot(user_preference, article_vector)
            norm_user = np.linalg.norm(user_preference)
            norm_article = np.linalg.norm(article_vector)

            if norm_user == 0 or norm_article == 0:
                similarity = 0.0
            else:
                similarity = float(dot_product / (norm_user * norm_article))

            similarities.append((article, similarity))

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.warning(f"유사도 계산 실패 (article {article.id}): {e}")
            # 유사도 0으로 처리
            similarities.append((article, 0.0))
            continue

    if not similarities:
        logger.info(f"User {user.id}: 유사도 계산 실패, 랜덤 선택")
        return random.choice(articles)

    # 3. 유사도 기준 정렬 (높은 순)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # 4. 상위 20%에서 가중 랜덤 선택 (다양성 확보)
    diversity_ratio = 0.2
    top_n = max(1, int(len(similarities) * diversity_ratio))
    top_candidates = similarities[:top_n]

    logger.info(f"AI 추천: 전체 {len(similarities)}개 중 상위 {top_n}개에서 선택")

    # 가중치 추출 및 정규화
    candidate_articles = [item[0] for item in top_candidates]
    candidate_weights = [item[1] for item in top_candidates]

    total_weight = sum(candidate_weights)
    if total_weight > 0:
        normalized_weights = [w / total_weight for w in candidate_weights]
    else:
        # 모든 가중치가 0이면 균등 확률
        normalized_weights = [1.0 / len(candidate_weights)] * len(candidate_weights)

    # 5. 가중 랜덤 선택
    selected_article = random.choices(
        candidate_articles, weights=normalized_weights, k=1
    )[0]

    # 선택된 게시글의 유사도 로깅
    selected_similarity = next(
        (sim for art, sim in top_candidates if art.id == selected_article.id), 0.0
    )
    logger.info(
        f"선택된 게시글: ID {selected_article.id}, 유사도 {selected_similarity:.3f}"
    )

    return selected_article


@extend_schema(
    methods=["GET"],
    tags=["draws"],
    summary="뽑기 기록 목록 조회",
    description="최근 5개의 뽑기 기록을 조회합니다.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "history": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "draw_id": {
                                "type": "integer",
                                "description": "뽑기 ID (1부터 시작)",
                            },
                            "article": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "title": {"type": "string"},
                                    "thumbnail": {"type": "string", "nullable": True},
                                    "category": {"type": "string", "nullable": True},
                                },
                            },
                            "place": {
                                "type": "object",
                                "properties": {
                                    "cid": {"type": "string"},
                                    "name": {"type": "string"},
                                    "address": {"type": "string"},
                                },
                            },
                            "drawn_at": {"type": "string", "format": "date-time"},
                        },
                    },
                },
                "total": {"type": "integer"},
                "limit": {"type": "integer"},
            },
        }
    },
)
@extend_schema(
    methods=["POST"],
    tags=["draws"],
    summary="게시글 뽑기 실행",
    description="랜덤 또는 AI 기반으로 게시글을 추천합니다. AI 모드는 사용자의 좋아요 기록을 분석하여 선호도에 맞는 게시글을 추천합니다.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "format": "float",
                    "description": "현재 위치 위도 (필수)",
                    "example": 37.5665,
                },
                "lng": {
                    "type": "number",
                    "format": "float",
                    "description": "현재 위치 경도 (필수)",
                    "example": 126.9780,
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "카테고리 목록 (선택)",
                    "example": ["카페", "음식점"],
                },
                "max_distance": {
                    "type": "integer",
                    "description": "최대 거리 km (선택, null이면 제한없음)",
                    "example": 5,
                },
                "mode": {
                    "type": "string",
                    "enum": ["random", "ai"],
                    "description": "추천 모드: random(완전랜덤), ai(사용자 선호도 기반)",
                    "example": "random",
                },
            },
            "required": ["lat", "lng"],
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "article": {
                    "type": "object",
                    "description": "뽑힌 게시글 정보",
                },
                "distance": {
                    "type": "number",
                    "format": "float",
                    "description": "현재 위치에서 거리 (km)",
                    "example": 2.3,
                },
                "draw_count": {
                    "type": "integer",
                    "description": "총 뽑기 횟수",
                    "example": 3,
                },
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "현재 위치 정보(lat, lng)는 필수입니다",
                }
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "조건에 맞는 게시글을 찾을 수 없습니다",
                },
                "retry_available": {"type": "boolean", "example": True},
            },
        },
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def draw_list_or_create(request):
    """
    GET /api/v1/draws/ - 기록 목록
    POST /api/v1/draws/ - 뽑기 실행
    """
    if request.method == "GET":
        return draw_list(request)
    elif request.method == "POST":
        return draw_create(request)


@extend_schema(
    methods=["GET"],
    tags=["draws"],
    summary="뽑기 기록 상세 조회",
    description="특정 뽑기 기록의 상세 정보를 조회합니다. draw_id는 1부터 시작합니다 (1이 가장 최근).",
    parameters=[
        OpenApiParameter(
            name="draw_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="뽑기 ID (1부터 시작, 1이 가장 최근)",
        )
    ],
)
@extend_schema(
    methods=["DELETE"],
    tags=["draws"],
    summary="뽑기 기록 삭제",
    description="특정 뽑기 기록을 삭제합니다. draw_id는 1부터 시작합니다 (1이 가장 최근).",
    parameters=[
        OpenApiParameter(
            name="draw_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="뽑기 ID (1부터 시작, 1이 가장 최근)",
        )
    ],
)
@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def draw_detail_or_destroy(request, draw_id):
    """
    GET /api/v1/draws/{draw_id}/ - 기록 상세
    DELETE /api/v1/draws/{draw_id}/ - 기록 삭제
    """
    if request.method == "GET":
        return draw_detail(request, draw_id)
    elif request.method == "DELETE":
        return draw_destroy(request, draw_id)


# ============================================
# POST /api/v1/draws/ - 뽑기 실행
# ============================================


@permission_classes([IsAuthenticated])
def draw_create(request):
    """
    랜덤 게시글 뽑기 실행
    POST /api/v1/draws/
    """
    # 필수 파라미터 검증
    lat = request.data.get("lat")
    lng = request.data.get("lng")

    if lat is None or lng is None:
        return Response(
            {"error": "현재 위치 정보(lat, lng)는 필수입니다"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return Response(
            {"error": "위도와 경도는 숫자여야 합니다"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 선택 파라미터
    categories = request.data.get("categories", [])
    max_distance = request.data.get("max_distance")
    mode = request.data.get("mode", "random")

    # 게시글 쿼리셋 생성 (발행된 게시글만)
    articles = Article.objects.filter(is_published=True).select_related("user", "place")

    # 카테고리 필터링
    if categories:
        category_filter = Q()
        for category in categories:
            category_filter |= Q(place__category_path__icontains=category)
        articles = articles.filter(category_filter)

    # 최근 5개 뽑기 기록과 중복 방지
    recent_article_ids = [
        draw.get("article_id")
        for draw in request.user.draw_history[:5]
        if draw.get("article_id")
    ]

    if recent_article_ids:
        articles = articles.exclude(id__in=recent_article_ids)

    # 거리 필터링
    if max_distance:
        filtered_articles = []
        for article in articles:
            if article.place and article.place.latitude and article.place.longitude:
                distance = calculate_distance(
                    lat,
                    lng,
                    float(article.place.latitude),
                    float(article.place.longitude),
                )
                if distance <= max_distance:
                    article.distance = distance
                    filtered_articles.append(article)
        articles = filtered_articles
    else:
        # 거리 제한 없을 때도 거리 계산
        articles_with_distance = []
        for article in articles:
            if article.place and article.place.latitude and article.place.longitude:
                article.distance = calculate_distance(
                    lat,
                    lng,
                    float(article.place.latitude),
                    float(article.place.longitude),
                )
                articles_with_distance.append(article)
        articles = articles_with_distance

    # 조건에 맞는 게시글이 없으면 에러
    if not articles:
        return Response(
            {"error": "조건에 맞는 게시글을 찾을 수 없습니다", "retry_available": True},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 추천 모드에 따라 게시글 선택
    if mode == "ai":
        # AI 기반 추천 (사용자 선호도 분석)
        selected_article = get_ai_recommended_article(request.user, articles)
    else:  # random
        # 완전 랜덤 선택
        selected_article = random.choice(articles)

    # 뽑기 기록 저장
    request.user.add_draw_history(
        cid=selected_article.place.cid if selected_article.place else None,
        article_id=selected_article.id,
    )

    # 응답
    serializer = ArticleDetailSerializer(selected_article, context={"request": request})

    response_data = {
        "article": serializer.data,
        "distance": getattr(selected_article, "distance", None),
        "draw_count": len(request.user.draw_history),
    }

    return Response(response_data, status=status.HTTP_201_CREATED)


# ============================================
# GET /api/v1/draws/ - 뽑기 기록 목록
# ============================================
@permission_classes([IsAuthenticated])
def draw_list(request):
    """
    뽑기 기록 목록 조회
    GET /api/v1/draws/
    """
    draw_history = request.user.draw_history[:5]

    history_data = []
    for index, draw in enumerate(draw_history):
        article_id = draw.get("article_id")
        cid = draw.get("cid")
        drawn_at = draw.get("drawn_at")

        # 게시글 정보
        article_info = None
        try:
            article = Article.objects.select_related("place").get(id=article_id)
            article_info = {
                "id": article.id,
                "title": article.title,
                "thumbnail": article.images[0] if article.images else None,
                "category": article.place.category_path if article.place else None,
            }
        except Article.DoesNotExist:
            pass

        # 장소 정보
        place_info = None
        if cid:
            try:
                place = Place.objects.get(cid=cid)
                place_info = {
                    "cid": place.cid,
                    "name": place.title,
                    "address": place.address_new or place.address,
                }
            except Place.DoesNotExist:
                pass

        history_data.append(
            {
                "draw_id": index + 1,  # 1부터 시작
                "article": article_info,
                "place": place_info,
                "drawn_at": drawn_at,
            }
        )

    return Response(
        {
            "history": history_data,
            "total": len(draw_history),
            "limit": 5,
        }
    )


# ============================================
# GET /api/v1/draws/{draw_id}/ - 기록 상세
# ============================================
@permission_classes([IsAuthenticated])
def draw_detail(request, draw_id):
    """
    뽑기 기록 상세 조회
    GET /api/v1/draws/{draw_id}/

    draw_id: 1부터 시작 (1이 가장 최근)
    """
    # 1-based를 0-based로 변환
    index = draw_id - 1

    # 범위 체크
    if index < 0 or index >= len(request.user.draw_history):
        return Response(
            {"error": "뽑기 기록을 찾을 수 없습니다"},
            status=status.HTTP_404_NOT_FOUND,
        )

    draw = request.user.draw_history[index]

    article_id = draw.get("article_id")
    cid = draw.get("cid")

    # 게시글 정보
    article_info = None
    try:
        article = Article.objects.select_related("place").get(id=article_id)
        article_info = {
            "id": article.id,
            "title": article.title,
            "thumbnail": article.images[0] if article.images else None,
            "category": article.place.category_path if article.place else None,
        }
    except Article.DoesNotExist:
        pass

    # 장소 정보
    place_info = None
    if cid:
        try:
            place = Place.objects.get(cid=cid)
            place_info = {
                "cid": place.cid,
                "name": place.title,
                "address": place.address_new or place.address,
            }
        except Place.DoesNotExist:
            pass

    return Response(
        {
            "draw_id": draw_id,
            "article": article_info,
            "place": place_info,
            "drawn_at": draw.get("drawn_at"),
        }
    )


# ============================================
# DELETE /api/v1/draws/{draw_id}/ - 기록 삭제
# ============================================
@permission_classes([IsAuthenticated])
def draw_destroy(request, draw_id):
    """
    뽑기 기록 삭제
    DELETE /api/v1/draws/{draw_id}/

    draw_id: 1부터 시작 (1이 가장 최근)
    """
    # 1-based를 0-based로 변환
    index = draw_id - 1

    # 범위 체크
    if index < 0 or index >= len(request.user.draw_history):
        return Response(
            {"error": "뽑기 기록을 찾을 수 없습니다"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 뽑기 기록 삭제
    request.user.draw_history.pop(index)
    request.user.save(update_fields=["draw_history"])

    return Response(status=status.HTTP_204_NO_CONTENT)
