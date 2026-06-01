# accounts/management/commands/create_test_users.py

import json
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "테스트 사용자 데이터 생성"

    def handle(self, *args, **options):
        # 기존 사용자 삭제
        User.objects.all().delete()

        # 프로필 이미지 만들기
        def get_default_avatar(user_nickname):
            AVATAR_STYLES = ["avataaars", "bottts", "fun-emoji", "pixel-art"]
            style = random.choice(AVATAR_STYLES)
            return f"https://api.dicebear.com/7.x/{style}/svg?seed={user_nickname}"

        greetings = [
            "서울의 숨은 명소를 찾아다니는 여행자입니다.",
            "경복궁부터 북촌까지, 서울 구석구석 탐방 중",
            "한강 공원을 사랑하는 사람입니다.",
            "익선동 골목길을 걷는 중입니다.",
            "남산타워에서 야경 보는 걸 좋아합니다.",
            "성수동 카페 투어 중 ☕",
            "서울 야경 명소를 찾아다닙니다.",
            "북촌 한옥마을 산책을 즐깁니다.",
            "DDP와 동대문 주변을 자주 갑니다.",
            "홍대 거리를 배회하는 중입니다.",
            "한남동 골목 탐험가",
            "서울숲 단골입니다.",
            "광장시장 먹방러",
            "서촌 동네를 구경 중입니다.",
            "창덕궁 후원 산책을 좋아합니다.",
            "여의도 한강공원 자전거 라이더",
            "경리단길을 걷는 중입니다.",
            "망원시장 탐방 중",
            "삼청동 갤러리 투어 중입니다.",
            "청계천 산책로를 따라 걷습니다.",
        ]

        names = [
            "강규민",
            "강인태",
            "강결한",
            "고민광",
            "김희소",
            "김민종",
            "김호준",
            "김훈치",
            "김아현",
            "나현성",
            "나현정",
            "박운영",
            "박아준",
            "박영찬",
            "백성우",
            "양서현",
            "여림희",
            "이우시",
            "정승환",
            "최선형",
        ]

        users_data = [
            {
                "username": f"user{idx+1}",
                "email": f"user{idx+1}@example.com",
                "password": "password123!",
                "nickname": names[idx],
                "bio": greetings[idx],
            }
            for idx in range(len(names))
        ]

        created_users = []
        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                nickname=user_data["nickname"],
                bio=user_data["bio"],
                profile_image=get_default_avatar(user_data["nickname"]),
            )
            created_users.append(user)
            self.stdout.write(self.style.SUCCESS(f"✓ 사용자 생성: {user.nickname}"))

        self.stdout.write(
            self.style.SUCCESS(f"\n총 {len(created_users)}명의 사용자 생성 완료!")
        )
