# server/articles/management/commands/dump_likes.py

import json
from datetime import datetime
from pathlib import Path

from articles.models import Like
from django.core.management.base import BaseCommand
from django.core.serializers import serialize


class Command(BaseCommand):
    help = "Like 데이터를 fixture로 덤프합니다 (UTF-8 인코딩 보장)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            help="출력 파일 경로 (예: fixtures/likes.json)",
        )
        parser.add_argument(
            "--timestamp",
            action="store_true",
            help="파일명에 타임스탬프 추가",
        )

    def handle(self, *args, **options):
        timestamp_flag = options["timestamp"]

        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if timestamp_flag else ""

        # 출력 파일 경로 결정
        if options["output"]:
            output_path = Path(options["output"])
        else:
            filename = f'likes_fixture{"_" + timestamp if timestamp else ""}.json'
            output_path = Path("articles/fixtures") / filename

        # fixtures 디렉토리 생성
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Like 데이터 가져오기
        self.stdout.write("LIKE 데이터 덤프 중...")
        queryset = Like.objects.all().order_by("pk")

        # JSON 직렬화
        serialized = serialize("json", queryset)
        data = json.loads(serialized)

        # 파일 저장
        self._save_to_file(data, output_path)

    def _save_to_file(self, data, output_path):
        """데이터를 파일로 저장"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,  # 한글 깨짐 방지
                    indent=2,
                )

            # 결과 출력
            file_size = output_path.stat().st_size / 1024  # KB
            count = len(data)

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Like 덤프 완료!\n"
                    f"  파일: {output_path}\n"
                    f"  개수: {count}개\n"
                    f"  크기: {file_size:.1f} KB\n"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ 덤프 실패: {str(e)}"))
