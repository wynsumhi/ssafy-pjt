"""
더미 데이터 생성 커맨드
기존 Article(2379개), Place(2428개) 데이터의 관계 필드만 채움

사용법:
    python manage.py generate_dummy_data
    python manage.py generate_dummy_data --comments 200 --likes 300
    python manage.py generate_dummy_data --reset  # 관계 데이터만 삭제 후 재생성
"""

import random

from accounts.models import Follow, User
from articles.models import Article, Comment, Like
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from places.models import Place


class Command(BaseCommand):
    help = "기존 데이터의 관계 필드 채우기 (작성자, 댓글, 좋아요, 팔로우, 저장한 장소)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--comments",
            type=int,
            default=150,
            help="생성할 댓글 수",
        )
        parser.add_argument(
            "--likes",
            type=int,
            default=200,
            help="생성할 좋아요 수",
        )
        parser.add_argument(
            "--follows",
            type=int,
            default=50,
            help="생성할 팔로우 관계 수",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="관계 데이터만 삭제 후 새로 생성 (Article, Place는 유지)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n=== 관계 데이터 생성 시작 ===\n"))

        # 초기화 옵션 (관계 데이터만 삭제, Article/Place는 유지)
        if options["reset"]:
            self.stdout.write(self.style.WARNING("기존 관계 데이터 삭제 중..."))
            Comment.objects.all().delete()
            Like.objects.all().delete()
            Follow.objects.all().delete()

            # Article의 user 필드만 null로
            Article.objects.update(user=None)

            # 사용자 관계 필드 초기화
            User.objects.all().update(draw_history=[], saved_places=[])
            self.stdout.write(self.style.SUCCESS("✓ 기존 관계 데이터 삭제 완료\n"))

        # 데이터 로드
        users = list(User.objects.all())
        places = list(Place.objects.all())
        articles = list(Article.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("ERROR: 사용자 데이터가 없습니다."))
            return

        if not places:
            self.stdout.write(self.style.ERROR("ERROR: 장소 데이터가 없습니다."))
            return

        if not articles:
            self.stdout.write(self.style.ERROR("ERROR: 게시글 데이터가 없습니다."))
            return

        self.stdout.write(f"사용자: {len(users)}명")
        self.stdout.write(f"장소: {len(places)}개")
        self.stdout.write(f"게시글: {len(articles)}개\n")

        # 1. 게시글 작성자 할당 (source=USER인 것만)
        self.assign_article_authors(users)

        # 2. 팔로우 관계 생성
        self.create_follows(users, options["follows"])

        # 3. 댓글 생성
        self.create_comments(users, options["comments"])

        # 4. 좋아요 생성
        self.create_likes(users, options["likes"])

        # 5. 저장한 장소 생성
        self.create_saved_places(users, places)

        # 6. 통계 업데이트
        self.update_statistics()

        self.stdout.write(self.style.SUCCESS("\n=== 관계 데이터 생성 완료 ===\n"))
        self.print_summary()

    def assign_article_authors(self, users):
        """기존 게시글 중 source=AI인 것에 랜덤 작성자 할당"""
        # AI 게시글은 user=null 유지
        ai_articles = Article.objects.filter(source="AI")
        count = 0

        for article in ai_articles:
            article.user = random.choice(users)
            article.save(update_fields=["user"])
            count += 1

        ai_count = Article.objects.filter(source="AI").count()
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ AI 게시글 {count}개에 작성자 할당 완료 (총 {ai_count}개)"
            )
        )

    def create_follows(self, users, count):
        """팔로우 관계 생성"""
        created = 0
        attempts = 0
        max_attempts = count * 3

        while created < count and attempts < max_attempts:
            follower = random.choice(users)
            following = random.choice(users)
            attempts += 1

            if follower == following:
                continue

            _, is_created = Follow.objects.get_or_create(
                follower=follower,
                following=following,
            )

            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"✓ 팔로우 관계 {created}개 생성 완료"))

    def create_comments(self, users, count):
        """댓글 생성 (1게시글 1댓글 원칙)"""
        articles = list(Article.objects.all())

        if not articles:
            self.stdout.write(
                self.style.WARNING("⚠ 게시글이 없어 댓글을 생성할 수 없습니다.")
            )
            return

        comment_templates = [
            "여기 정말 좋아요!",
            "저도 가봤는데 최고였어요.",
            "다음에 꼭 가봐야겠네요.",
            "추천 감사합니다!",
            "사진이 너무 예뻐요.",
            "분위기 좋아 보이네요.",
            "저장해둡니다 ㅎㅎ",
            "궁금했는데 정보 감사해요.",
        ]

        created = 0
        attempts = 0
        max_attempts = count * 3

        while created < count and attempts < max_attempts:
            article = random.choice(articles)
            user = random.choice(users)
            attempts += 1

            # 본인 게시글에는 댓글 안 달기
            if article.user == user:
                continue

            # 이미 댓글 달았으면 스킵 (1게시글 1댓글)
            if Comment.objects.filter(article=article, user=user).exists():
                continue

            Comment.objects.create(
                article=article,
                user=user,
                content=random.choice(comment_templates),
                is_anonymous=True,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"✓ 댓글 {created}개 생성 완료"))

    def create_likes(self, users, count):
        """좋아요 생성"""
        articles = list(Article.objects.all())

        if not articles:
            self.stdout.write(
                self.style.WARNING("⚠ 게시글이 없어 좋아요를 생성할 수 없습니다.")
            )
            return

        created = 0
        attempts = 0
        max_attempts = count * 3

        while created < count and attempts < max_attempts:
            article = random.choice(articles)
            user = random.choice(users)
            attempts += 1

            # 본인 게시글에는 좋아요 안 하기
            if article.user == user:
                continue

            _, is_created = Like.objects.get_or_create(
                user=user,
                article=article,
            )

            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"✓ 좋아요 {created}개 생성 완료"))

    def create_saved_places(self, users, places):
        """각 사용자의 저장한 장소 생성 (최대 10개)"""
        total_saved = 0

        for user in users:
            # 각 사용자당 3~10개 랜덤 저장
            save_count = min(random.randint(3, 10), len(places))
            saved_cids = random.sample([p.cid for p in places], k=save_count)

            user.saved_places = saved_cids
            user.save(update_fields=["saved_places"])
            total_saved += len(saved_cids)

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ 저장한 장소 총 {total_saved}개 생성 완료 "
                f"(사용자당 평균 {total_saved//len(users)}개)"
            )
        )

    def update_statistics(self):
        """게시글 통계 업데이트"""
        articles = Article.objects.all()

        for article in articles:
            article.comment_count = article.comments.count()
            article.like_count = article.likes.count()
            article.save(update_fields=["comment_count", "like_count"])

        self.stdout.write(self.style.SUCCESS(f"✓ 게시글 통계 업데이트 완료"))

    def print_summary(self):
        """생성 결과 요약"""
        article_count = Article.objects.count()
        user_article_count = Article.objects.filter(source="USER").count()
        ai_article_count = Article.objects.filter(source="AI").count()
        comment_count = Comment.objects.count()
        like_count = Like.objects.count()
        follow_count = Follow.objects.count()

        total_saved = sum(len(user.saved_places) for user in User.objects.all())

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("📊 생성 결과 요약"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"총 게시글: {article_count}개")
        self.stdout.write(f"  - 사용자 게시글: {user_article_count}개")
        self.stdout.write(f"  - AI 게시글: {ai_article_count}개")
        self.stdout.write(f"총 댓글: {comment_count}개")
        self.stdout.write(f"총 좋아요: {like_count}개")
        self.stdout.write(f"총 팔로우: {follow_count}개")
        self.stdout.write(f"총 저장한 장소: {total_saved}개")
        self.stdout.write("=" * 50 + "\n")
