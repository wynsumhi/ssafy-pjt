# server/recommendations/services/algorithm.py

import numpy as np
from django.db.models import Q, Count, Avg
from typing import List, Optional, Tuple
import random
import logging

logger = logging.getLogger(__name__)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    코사인 유사도 계산
    
    Args:
        vec1: 첫 번째 벡터
        vec2: 두 번째 벡터
        
    Returns:
        float: 유사도 (0~1)
    """
    if vec1.size == 0 or vec2.size == 0:
        return 0.0
    
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(dot_product / (norm_a * norm_b))


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Haversine 공식을 사용한 두 지점 간 거리 계산
    
    Args:
        lat1, lng1: 첫 번째 지점의 위도, 경도
        lat2, lng2: 두 번째 지점의 위도, 경도
        
    Returns:
        float: 거리 (km)
    """
    from math import radians, cos, sin, asin, sqrt
    
    # 라디안으로 변환
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    
    # Haversine 공식
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    
    # 지구 반지름 (km)
    r = 6371
    
    return c * r


def get_user_preference_vector(user) -> Optional[np.ndarray]:
    """
    사용자 선호도 벡터 계산
    - 좋아요한 게시글들의 임베딩 평균 사용
    - 최소 3개 이상의 데이터 필요
    
    Args:
        user: User 모델 인스턴스
        
    Returns:
        Optional[np.ndarray]: 선호도 벡터 또는 None
    """
    from articles.models import Article
    
    # 좋아요한 게시글 조회
    liked_articles = Article.objects.filter(
        likes__user=user,
        embedding_vector__isnull=False
    ).exclude(
        embedding_vector=[]
    ).order_by('-likes__created_at')[:20]  # 최근 20개
    
    if liked_articles.count() < 3:
        logger.info(f"User {user.id} has insufficient liked articles for preference vector")
        return None
    
    # 임베딩 벡터 수집
    embeddings = []
    for article in liked_articles:
        try:
            embedding = np.array(article.embedding_vector, dtype=np.float32)
            if embedding.size > 0:
                embeddings.append(embedding)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid embedding for article {article.id}: {e}")
            continue
    
    if len(embeddings) < 3:
        return None
    
    # 가중 평균 (최근 것에 더 높은 가중치)
    weights = np.linspace(0.5, 1.0, len(embeddings))
    weighted_avg = np.average(embeddings, axis=0, weights=weights)
    
    return weighted_avg


def filter_articles_by_conditions(
    categories: List[str] = None,
    max_distance: float = None,
    user_lat: float = None,
    user_lng: float = None,
    exclude_article_ids: List[int] = None,
    min_quality_score: float = None
):
    """
    조건에 맞는 게시글 필터링
    
    Args:
        categories: 카테고리 리스트
        max_distance: 최대 거리 (km)
        user_lat: 사용자 위도
        user_lng: 사용자 경도
        exclude_article_ids: 제외할 게시글 ID 리스트
        min_quality_score: 최소 품질 점수
        
    Returns:
        QuerySet: 필터링된 게시글 쿼리셋
    """
    from articles.models import Article
    
    # 기본 필터: 발행된 게시글, 임베딩 있는 것만
    queryset = Article.objects.filter(
        is_published=True,
        embedding_vector__isnull=False
    ).exclude(
        embedding_vector=[]
    ).select_related('place', 'user')
    
    # 제외할 게시글
    if exclude_article_ids:
        queryset = queryset.exclude(id__in=exclude_article_ids)
    
    # 카테고리 필터
    if categories and len(categories) > 0:
        category_filter = Q()
        for category in categories:
            category_filter |= Q(place__category_path__icontains=category)
        queryset = queryset.filter(category_filter)
    
    # 품질 점수 필터
    if min_quality_score is not None:
        queryset = queryset.filter(quality_score__gte=min_quality_score)
    
    # 거리 필터 (장소 위치 정보가 있는 경우)
    if max_distance and user_lat and user_lng:
        # 위도/경도가 있는 장소만 필터링
        queryset = queryset.filter(
            place__latitude__isnull=False,
            place__longitude__isnull=False
        )
        
        # 거리 계산은 Python에서 수행 (PostgreSQL PostGIS 없이)
        # TODO: 성능 최적화 필요시 PostGIS 사용 고려
    
    return queryset


def get_random_article(
    categories: List[str] = None,
    max_distance: float = None,
    user_lat: float = None,
    user_lng: float = None,
    exclude_article_ids: List[int] = None
):
    """
    완전 랜덤 추천
    
    Args:
        categories: 카테고리 리스트
        max_distance: 최대 거리 (km)
        user_lat: 사용자 위도
        user_lng: 사용자 경도
        exclude_article_ids: 제외할 게시글 ID 리스트
        
    Returns:
        Tuple[Optional[Article], Optional[float]]: (게시글, 거리)
    """
    queryset = filter_articles_by_conditions(
        categories=categories,
        max_distance=max_distance,
        user_lat=user_lat,
        user_lng=user_lng,
        exclude_article_ids=exclude_article_ids
    )
    
    # 거리 필터링 (Python에서 처리)
    candidates = []
    for article in queryset:
        if max_distance and user_lat and user_lng:
            if article.place.latitude and article.place.longitude:
                distance = calculate_distance(
                    user_lat, user_lng,
                    float(article.place.latitude),
                    float(article.place.longitude)
                )
                if distance <= max_distance:
                    candidates.append((article, distance))
        else:
            candidates.append((article, None))
    
    if not candidates:
        logger.info("No articles found matching the criteria")
        return None, None
    
    # 랜덤 선택
    selected = random.choice(candidates)
    logger.info(f"Random article selected: {selected[0].id}")
    
    return selected


def get_ai_recommended_article(
    user,
    categories: List[str] = None,
    max_distance: float = None,
    user_lat: float = None,
    user_lng: float = None,
    exclude_article_ids: List[int] = None,
    diversity_ratio: float = 0.2
):
    """
    AI 기반 추천
    - 사용자 선호도 벡터와 게시글 임베딩의 유사도 계산
    - 상위 N%에서 가중 랜덤 선택 (다양성 확보)
    
    Args:
        user: User 모델 인스턴스
        categories: 카테고리 리스트
        max_distance: 최대 거리 (km)
        user_lat: 사용자 위도
        user_lng: 사용자 경도
        exclude_article_ids: 제외할 게시글 ID 리스트
        diversity_ratio: 상위 몇 %에서 선택할지 (0.2 = 상위 20%)
        
    Returns:
        Tuple[Optional[Article], Optional[float]]: (게시글, 거리)
    """
    # 사용자 선호도 벡터 계산
    user_preference = get_user_preference_vector(user)
    
    # 데이터 부족시 랜덤으로 폴백
    if user_preference is None:
        logger.info(f"User {user.id} preference vector not available, falling back to random")
        return get_random_article(
            categories=categories,
            max_distance=max_distance,
            user_lat=user_lat,
            user_lng=user_lng,
            exclude_article_ids=exclude_article_ids
        )
    
    # 후보 게시글 필터링
    queryset = filter_articles_by_conditions(
        categories=categories,
        max_distance=max_distance,
        user_lat=user_lat,
        user_lng=user_lng,
        exclude_article_ids=exclude_article_ids
    )
    
    # 유사도 계산
    similarities = []
    for article in queryset:
        try:
            article_vector = np.array(article.embedding_vector, dtype=np.float32)
            similarity = cosine_similarity(user_preference, article_vector)
            
            # 거리 계산
            distance = None
            if user_lat and user_lng and article.place.latitude and article.place.longitude:
                distance = calculate_distance(
                    user_lat, user_lng,
                    float(article.place.latitude),
                    float(article.place.longitude)
                )
                
                # 거리 제한 확인
                if max_distance and distance > max_distance:
                    continue
            
            similarities.append((article, similarity, distance))
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error processing article {article.id}: {e}")
            continue
    
    if not similarities:
        logger.info("No articles found matching the criteria")
        return None, None
    
    # 유사도 기준 정렬 (높은 순)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # 상위 N%에서 선택 (다양성 확보)
    top_n = max(1, int(len(similarities) * diversity_ratio))
    top_candidates = similarities[:top_n]
    
    logger.info(f"AI recommendation: {len(similarities)} candidates, selecting from top {top_n}")
    
    # 가중 랜덤 선택 (유사도가 높을수록 선택 확률 높음)
    articles = [item[0] for item in top_candidates]
    weights = [item[1] for item in top_candidates]
    distances = [item[2] for item in top_candidates]
    
    # 가중치 정규화
    total_weight = sum(weights)
    if total_weight > 0:
        normalized_weights = [w / total_weight for w in weights]
    else:
        normalized_weights = [1.0 / len(weights)] * len(weights)
    
    # 선택
    selected_idx = random.choices(range(len(articles)), weights=normalized_weights, k=1)[0]
    selected_article = articles[selected_idx]
    selected_distance = distances[selected_idx]
    
    logger.info(f"AI recommended article: {selected_article.id} (similarity: {weights[selected_idx]:.3f})")
    
    return selected_article, selected_distance