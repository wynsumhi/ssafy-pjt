# accounts/management/commands/dump_users.py

import json
import os

from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "사용자 데이터를 JSON fixture로 덤프 (UTF-8)"

    def handle(self, *args, **options):
        # fixtures 디렉토리 생성
        fixtures_dir = "accounts/fixtures"
        os.makedirs(fixtures_dir, exist_ok=True)

        # 사용자 데이터 가져오기
        users = User.objects.all()

        # JSON으로 직렬화
        data = serializers.serialize(
            "json", users, indent=2, use_natural_foreign_keys=True
        )

        # UTF-8로 파일 저장
        output_path = os.path.join(fixtures_dir, "users.json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data)

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ {users.count()}명의 사용자 데이터를 {output_path}에 저장했습니다."
            )
        )
