# server/recommendations/management/commands/generate_embeddings.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from articles.models import Article
from places.models import Place
from recommendations.services.embedding import embedding_service
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate embeddings for articles and places using sentence-transformers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            default='both',
            choices=['article', 'place', 'both'],
            help='Which model to generate embeddings for'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=32,
            help='Batch size for embedding generation'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate embeddings even if they already exist'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting embedding generation...'))
        
        if options['model'] in ['article', 'both']:
            self.generate_article_embeddings(
                batch_size=options['batch_size'],
                force=options['force']
            )
        
        if options['model'] in ['place', 'both']:
            self.generate_place_embeddings(
                batch_size=options['batch_size'],
                force=options['force']
            )
        
        self.stdout.write(self.style.SUCCESS('All embeddings generated successfully!'))

    def generate_article_embeddings(self, batch_size: int, force: bool):
        """게시글 임베딩 생성"""
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.WARNING('Generating article embeddings...'))
        
        # 임베딩이 없는 게시글 조회
        if force:
            articles = Article.objects.filter(is_published=True)
        else:
            articles = Article.objects.filter(
                Q(embedding_vector__isnull=True) | Q(embedding_vector=[]),
                is_published=True
            )
        
        total = articles.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✓ No articles to process'))
            return
        
        self.stdout.write(f'Processing {total} articles...')
        
        # 배치 처리
        success_count = 0
        error_count = 0
        
        for i in tqdm(range(0, total, batch_size), desc="Articles"):
            batch = list(articles[i:i+batch_size])
            
            try:
                # 텍스트 생성
                texts = [
                    embedding_service.generate_article_text(article)
                    for article in batch
                ]
                
                # 임베딩 생성
                embeddings = embedding_service.encode_batch(texts, batch_size=batch_size)
                
                # DB 저장
                for article, embedding in zip(batch, embeddings):
                    article.embedding_vector = embedding
                    article.save(update_fields=['embedding_vector'])
                    success_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing batch: {e}')
                )
                error_count += len(batch)
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Article embeddings: {success_count} succeeded, {error_count} failed'
        ))

    def generate_place_embeddings(self, batch_size: int, force: bool):
        """장소 임베딩 생성"""
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.WARNING('Generating place embeddings...'))
        
        # 임베딩이 없는 장소 조회
        if force:
            places = Place.objects.all()
        else:
            places = Place.objects.filter(
                Q(embedding_vector__isnull=True) | Q(embedding_vector=[])
            )
        
        total = places.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✓ No places to process'))
            return
        
        self.stdout.write(f'Processing {total} places...')
        
        # 배치 처리
        success_count = 0
        error_count = 0
        
        for i in tqdm(range(0, total, batch_size), desc="Places"):
            batch = list(places[i:i+batch_size])
            
            try:
                # 텍스트 생성
                texts = [
                    embedding_service.generate_place_text(place)
                    for place in batch
                ]
                
                # 임베딩 생성
                embeddings = embedding_service.encode_batch(texts, batch_size=batch_size)
                
                # DB 저장
                for place, embedding in zip(batch, embeddings):
                    place.embedding_vector = embedding
                    place.save(update_fields=['embedding_vector'])
                    success_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing batch: {e}')
                )
                error_count += len(batch)
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Place embeddings: {success_count} succeeded, {error_count} failed'
        ))s