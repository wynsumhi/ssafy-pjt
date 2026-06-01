# server/recommendations/services/embedding.py

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """임베딩 생성 서비스"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """싱글톤 패턴 - 모델을 한 번만 로드"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """모델 초기화"""
        if self._model is None:
            logger.info("Loading sentence-transformers model...")
            self._model = SentenceTransformer('jhgan/ko-sroberta-multitask')
            logger.info("Model loaded successfully")
    
    def generate_article_text(self, article) -> str:
        """
        게시글에서 임베딩용 텍스트 생성
        
        Args:
            article: Article 모델 인스턴스
            
        Returns:
            str: 결합된 텍스트
        """
        text_parts = []
        
        # 제목 (필수)
        if article.title:
            text_parts.append(article.title)
        
        # 내용 (최대 500자)
        if article.content:
            content = article.content[:500]
            text_parts.append(content)
        
        # 태그
        if article.tags:
            text_parts.extend(article.tags)
        
        # 장소 정보 추가
        if article.place:
            if article.place.title:
                text_parts.append(article.place.title)
            if article.place.category_path:
                text_parts.append(article.place.category_path)
        
        return ' '.join(text_parts)
    
    def generate_place_text(self, place) -> str:
        """
        장소에서 임베딩용 텍스트 생성
        
        Args:
            place: Place 모델 인스턴스
            
        Returns:
            str: 결합된 텍스트
        """
        text_parts = []
        
        # 제목 (필수)
        if place.title:
            text_parts.append(place.title)
        
        # 요약 (최대 300자)
        if place.summary:
            summary = place.summary[:300]
            text_parts.append(summary)
        
        # 카테고리
        if place.category_path:
            text_parts.append(place.category_path)
        
        # 태그
        if place.tags:
            text_parts.extend(place.tags)
        
        return ' '.join(text_parts)
    
    def encode(self, text: str) -> List[float]:
        """
        텍스트를 임베딩 벡터로 변환
        
        Args:
            text: 입력 텍스트
            
        Returns:
            List[float]: 임베딩 벡터 (768차원)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for encoding")
            return [0.0] * 768
        
        try:
            embedding = self._model.encode(text, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return [0.0] * 768
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        여러 텍스트를 배치로 임베딩 벡터로 변환
        
        Args:
            texts: 입력 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            List[List[float]]: 임베딩 벡터 리스트
        """
        if not texts:
            return []
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error encoding batch: {e}")
            return [[0.0] * 768 for _ in texts]
    
    def generate_article_embedding(self, article) -> List[float]:
        """
        게시글의 임베딩 벡터 생성
        
        Args:
            article: Article 모델 인스턴스
            
        Returns:
            List[float]: 임베딩 벡터
        """
        text = self.generate_article_text(article)
        return self.encode(text)
    
    def generate_place_embedding(self, place) -> List[float]:
        """
        장소의 임베딩 벡터 생성
        
        Args:
            place: Place 모델 인스턴스
            
        Returns:
            List[float]: 임베딩 벡터
        """
        text = self.generate_place_text(place)
        return self.encode(text)


# 싱글톤 인스턴스
embedding_service = EmbeddingService()