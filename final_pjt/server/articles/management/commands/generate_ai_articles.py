# server/articles/management/commands/generate_ai_articles.py
import json
import os
import time

from django.core.management.base import BaseCommand
from django.db import transaction

import requests

from articles.models import Article
from places.models import Place


class Command(BaseCommand):
    help = "AI 게시글 생성 (GPT-4o Mini)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=None, help="생성할 게시글 수 제한 (테스트용)"
        )
        parser.add_argument("--batch-size", type=int, default=50, help="배치 처리 단위")
        parser.add_argument("--delay", type=float, default=0.5, help="API 호출 간 딜레이 (초)")

    def handle(self, *args, **options):
        limit = options["limit"]
        batch_size = options["batch_size"]
        delay = options["delay"]

        # API 설정
        api_url = os.getenv("GMS_API_URL")
        api_key = os.getenv("GMS_API_KEY")

        if not api_url or not api_key:
            self.stdout.write(self.style.ERROR("API URL 또는 KEY가 설정되지 않았습니다."))
            return

        # 이미 AI 게시글이 있는 장소 제외
        existing_cids = Article.objects.filter(source="AI").values_list("place_id", flat=True)
        places = Place.objects.exclude(cid__in=existing_cids).order_by("cid")

        if limit:
            places = places[:limit]

        total = places.count()
        self.stdout.write(self.style.SUCCESS(f"총 {total}개 장소에 대해 AI 게시글 생성 시작"))

        # 시작 시간 기록
        start_time = time.time()
        success_count = 0
        fail_count = 0
        failed_cids = []

        for i, place in enumerate(places, 1):
            try:
                # 진행률 표시
                if i % 10 == 0 or i == 1:
                    self.stdout.write(f"진행: {i}/{total} ({i/total*100:.1f}%)")

                # AI 게시글 생성
                article_data = self.generate_article(place, api_url, api_key)

                if article_data:
                    # Article 저장
                    with transaction.atomic():
                        Article.objects.create(
                            place=place,  # Place 인스턴스 전달
                            user=None,  # AI 작성
                            title=article_data["title"],
                            content=article_data["content"],
                            tags=article_data["tags"],
                            source="AI",
                            generation_metadata={
                                "model": "gpt-4o-mini",
                                "temperature": 1,
                                "place_title": place.title,
                                "place_category": place.category_path,
                            },
                            is_published=True,
                        )
                    success_count += 1
                else:
                    fail_count += 1
                    failed_cids.append(place.cid)
                    self.stdout.write(self.style.WARNING(f"실패: {place.title} (CID: {place.cid})"))

                # 배치마다 진행 상황 출력
                if i % batch_size == 0:
                    self.stdout.write(
                        self.style.SUCCESS(f"배치 완료: 성공 {success_count}, 실패 {fail_count}")
                    )

                # API 호출 딜레이
                time.sleep(delay)

            except Exception as e:
                fail_count += 1
                failed_cids.append(place.cid)
                self.stdout.write(self.style.ERROR(f"오류 발생: {place.title} - {str(e)}"))

        # 최종 결과
        self.stdout.write(self.style.SUCCESS("=" * 50))

        # 소요 시간 계산 (추가)
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.stdout.write(self.style.SUCCESS(f"소요 시간: {minutes}분 {seconds}초"))
        self.stdout.write(self.style.SUCCESS(f"평균 시간: {elapsed_time/total:.2f}초/개"))

        self.stdout.write(self.style.SUCCESS(f"완료: 성공 {success_count}, 실패 {fail_count}"))

        if failed_cids:
            self.stdout.write(
                self.style.WARNING(f'실패한 CID 목록: {", ".join(failed_cids[:10])}...')
            )

    def generate_article(self, place, api_url, api_key):
        """GMS API를 호출하여 게시글 생성"""

        # 프롬프트 구성
        prompt = self.build_prompt(place)

        try:
            response = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 서울의 다양한 장소를 직접 방문하고 솔직한 후기를 작성하는 여행 블로거입니다. 실제 사람이 쓴 것처럼 자연스럽고 생생한 글을 작성해주세요.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 1,
                    "max_completion_tokens": 3000,
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()

                # 전체 응답 출력 (디버깅)
                import json as json_module

                self.stdout.write(self.style.WARNING("=" * 50))
                self.stdout.write(self.style.WARNING("API 전체 응답:"))
                self.stdout.write(
                    self.style.WARNING(json_module.dumps(result, indent=2, ensure_ascii=False))
                )
                self.stdout.write(self.style.WARNING("=" * 50))

                # 응답 구조 확인
                if "choices" not in result or len(result["choices"]) == 0:
                    self.stdout.write(self.style.ERROR(f"잘못된 응답 구조: {result}"))
                    return None

                content = result["choices"][0]["message"]["content"]

                # content 값 출력 (디버깅)
                self.stdout.write(self.style.WARNING(f"Content 타입: {type(content)}"))
                self.stdout.write(self.style.WARNING(f'Content 값: "{content}"'))
                self.stdout.write(
                    self.style.WARNING(f"Content 길이: {len(content) if content else 0}")
                )

                # 빈 응답 체크
                if not content or not content.strip():
                    self.stdout.write(self.style.ERROR("빈 응답 받음"))
                    return None

                # 디버깅: 원본 응답 출력
                self.stdout.write(f"  API 응답: {content[:200]}...")

                # JSON 파싱
                # GPT가 ```json ``` 로 감쌀 수 있으므로 제거
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                article_data = json.loads(content)

                # 검증
                if self.validate_article(article_data):
                    return article_data
                else:
                    return None
            else:
                self.stdout.write(
                    self.style.ERROR(f"API 오류: {response.status_code} - {response.text}")
                )
                return None

        except requests.exceptions.Timeout:
            self.stdout.write(self.style.ERROR("API 타임아웃"))
            return None
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"JSON 파싱 오류: {str(e)}"))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"예상치 못한 오류: {str(e)}"))
            return None

    def build_prompt(self, place):
        """장소 정보를 바탕으로 프롬프트 구성"""

        tags_str = ", ".join(place.tags) if place.tags else "없음"

        # description이 너무 길면 summary만 사용
        place_info = place.summary or "정보 없음"
        if place.description and len(place.description) < 500:
            place_info = place.description

        prompt = f"""장소: {place.title}
카테고리: {place.category_path}
설명: {place_info[:200]}

500-700자 방문 후기를 JSON으로 작성하세요.

출력:
{{
  "title": "제목 (20자 이내)",
  "content": "본문 (500-700자)",
  "tags": ["태그1", "태그2", "태그3"]
}}"""
        return prompt

    def validate_article(self, article_data):
        """생성된 게시글 데이터 검증"""

        if not isinstance(article_data, dict):
            return False

        required_fields = ["title", "content", "tags"]
        for field in required_fields:
            if field not in article_data:
                return False

        # 제목 길이 검증
        if len(article_data["title"]) > 50 or len(article_data["title"]) < 5:
            return False

        # 본문 길이 검증
        if len(article_data["content"]) < 100 or len(article_data["content"]) > 3000:
            return False

        # 태그 검증
        if not isinstance(article_data["tags"], list) or len(article_data["tags"]) > 5:
            return False

        return True
