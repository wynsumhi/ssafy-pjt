# server/articles/management/commands/update_embeddings.py

import json

from articles.models import Article
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "기존 Article 데이터에 임베딩 벡터를 업데이트합니다"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            type=str,
            default="articles_fixture_v2.json",
            help="임베딩 벡터가 포함된 fixture 파일 경로",
        )

    def handle(self, *args, **options):
        fixture_path = options["fixture"]

        try:
            # Fixture 파일 읽기
            with open(fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            updated_count = 0
            skipped_count = 0
            error_count = 0

            for item in data:
                if item["model"] != "articles.article":
                    continue

                pk = item["pk"]
                embedding_vector = item["fields"].get("embedding_vector")

                # 임베딩 벡터가 없으면 스킵
                if not embedding_vector or embedding_vector == "null":
                    skipped_count += 1
                    continue

                try:
                    # Article 조회
                    article = Article.objects.get(pk=pk)

                    # 이미 임베딩이 있으면 스킵 (선택사항)
                    if article.embedding_vector and len(article.embedding_vector) > 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Article {pk}: 이미 임베딩 벡터가 존재합니다 (스킵)"
                            )
                        )
                        skipped_count += 1
                        continue

                    # JSON 문자열을 리스트로 변환
                    if isinstance(embedding_vector, str):
                        embedding_vector = json.loads(embedding_vector)

                    # 임베딩 벡터 업데이트
                    article.embedding_vector = embedding_vector
                    article.save(update_fields=["embedding_vector"])

                    self.stdout.write(
                        self.style.SUCCESS(f"Article {pk}: 임베딩 벡터 업데이트 완료")
                    )
                    updated_count += 1

                except Article.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Article {pk}: 존재하지 않는 게시글")
                    )
                    error_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Article {pk}: 오류 발생 - {str(e)}")
                    )
                    error_count += 1

            # 결과 출력
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n=== 임베딩 벡터 업데이트 완료 ==="
                    f"\n업데이트: {updated_count}개"
                    f"\n스킵: {skipped_count}개"
                    f"\n오류: {error_count}개"
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Fixture 파일을 찾을 수 없습니다: {fixture_path}")
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR("Fixture 파일의 JSON 형식이 올바르지 않습니다")
            )
