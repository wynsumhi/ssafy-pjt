from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    지구깡 사용자 모델
    Django 기본 User를 확장하여 추가 필드 구현
    """

    # 기본 필드 (AbstractUser에서 상속)
    # username, email, password, first_name, last_name, is_staff, is_active, date_joined

    # 추가 필드
    nickname = models.CharField(
        max_length=50, unique=True, verbose_name="닉네임", null=True, blank=True
    )

    profile_image = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="프로필 이미지"
    )

    bio = models.TextField(blank=True, null=True, verbose_name="소개글")

    # 최대 5개 제한, 임시 데이터이므로 JSON으로 관리 (최대 5개) - JSONB
    draw_history = models.JSONField(
        default=list,
        blank=True,
        verbose_name="뽑기 기록",
        help_text='[{"cid": "...", "article_id": 123, "drawn_at": "2024-12-01T10:30:00Z"}, ...]',
    )

    # 최대 10개 제한, 단방향 조회만 필요하므로 JSON으로 관리- Array
    saved_places = models.JSONField(
        default=list,
        blank=True,
        verbose_name="저장한 장소",
        help_text='["cid1", "cid2", ...]',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="가입일")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nickname} ({self.email})"

    # 헬퍼 메서드
    def add_draw_history(self, cid, article_id):
        """뽑기 기록 추가 (최대 5개 유지)"""
        from django.utils import timezone

        history_item = {
            "cid": cid,
            "article_id": article_id,
            "drawn_at": timezone.now().isoformat(),
        }

        # 기존 기록에 추가
        self.draw_history.insert(0, history_item)

        # 5개 초과 시 오래된 것 삭제
        if len(self.draw_history) > 5:
            self.draw_history = self.draw_history[:5]

        self.save(update_fields=["draw_history"])

    def add_saved_place(self, cid):
        """장소 저장 (최대 10개)"""
        if cid in self.saved_places:
            return False, "이미 저장된 장소입니다"

        if len(self.saved_places) >= 10:
            return False, "저장 가능한 최대 개수(10개)를 초과했습니다"

        self.saved_places.append(cid)
        self.save(update_fields=["saved_places"])
        return True, "장소가 저장되었습니다"

    def remove_saved_place(self, cid):
        """저장한 장소 삭제"""
        if cid in self.saved_places:
            self.saved_places.remove(cid)
            self.save(update_fields=["saved_places"])
            return True
        return False


class Follow(models.Model):
    """팔로우 관계 모델"""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", verbose_name="팔로워"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers", verbose_name="팔로잉"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="팔로우 시작일")

    class Meta:
        db_table = "follows"
        verbose_name = "팔로우"
        verbose_name_plural = "팔로우"
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow_relationship"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="prevent_self_follow",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.nickname} → {self.following.nickname}"
