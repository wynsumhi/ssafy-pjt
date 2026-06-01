# server/places/management/commands/fetch_place_details.py
import os
import time
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

import requests

from places.models import Place, PlaceCID


class Command(BaseCommand):
    help = "수집된 CID로 장소 상세 정보 조회"

    API_BASE_URL = "https://api-call.visitseoul.net/api/v1/contents/info"
    API_KEY = os.getenv("VISIT_SEOUL_API_KEY")

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100, help="한 번에 처리할 CID 개수")
        parser.add_argument("--retry-errors", action="store_true", help="이전에 실패한 CID 재시도")
        parser.add_argument("--delay", type=float, default=1.5, help="요청 간 대기 시간(초)")

    def handle(self, *args, **options):
        if not self.API_KEY:
            self.stdout.write(self.style.ERROR("VISIT_SEOUL_API_KEY가 설정되지 않았습니다."))
            return

        batch_size = options["batch_size"]
        retry_errors = options["retry_errors"]
        delay = options["delay"]

        # 미수집 CID 조회
        queryset = PlaceCID.objects.filter(is_fetched=False)
        if not retry_errors:
            queryset = queryset.filter(fetch_error="")

        pending_cids = queryset.order_by("created_at")[:batch_size]

        total = pending_cids.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("수집할 CID가 없습니다."))
            return

        self.stdout.write(f"\n{total}개 CID 상세정보 수집 시작...\n")
        self.stdout.write(f"요청 간격: {delay}초\n")

        success_count = 0
        error_count = 0

        for idx, cid_obj in enumerate(pending_cids, 1):
            self.stdout.write(f"[{idx}/{total}] {cid_obj.cid} 처리 중...")

            try:
                detail_data = self.fetch_detail_with_retry(cid_obj.cid, max_retries=3)

                if detail_data:
                    self.save_place(cid_obj.cid, detail_data)
                    cid_obj.is_fetched = True
                    cid_obj.fetch_error = ""
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS("  → 성공"))
                else:
                    cid_obj.fetch_error = "API 응답 없음"
                    error_count += 1
                    self.stdout.write(self.style.WARNING("  → 실패: API 응답 없음"))

            except Exception as e:
                cid_obj.fetch_error = str(e)
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  → 실패: {e}"))

            finally:
                cid_obj.fetch_attempted_at = timezone.now()
                cid_obj.save()

                # 마지막 요청이 아니면 대기
                if idx < total:
                    time.sleep(delay)

                # time.sleep(1.5)

        self.stdout.write(
            self.style.SUCCESS(f"\n완료: 성공 {success_count}, 실패 {error_count} / 전체 {total}")
        )

    def fetch_detail_with_retry(self, cid, max_retries=3):
        """재시도 로직이 포함된 API 요청"""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.API_BASE_URL,
                    headers={
                        "VISITSEOUL-API-KEY": self.API_KEY,
                        "Accept": "application/json;charset=UTF-8",
                        "Content-Type": "application/json;charset=UTF-8",
                    },
                    json={"cid": cid},
                    timeout=30,
                )

                # 500 에러인 경우 재시도
                if response.status_code == 500:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 2초, 4초, 6초
                        self.stdout.write(
                            f"    500 에러 - {wait_time}초 후 재시도 ({attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("500 Server Error (최대 재시도 초과)")

                response.raise_for_status()
                return response.json().get("data")

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    self.stdout.write(f"    타임아웃 - 3초 후 재시도 ({attempt + 1}/{max_retries})")
                    time.sleep(3)
                    continue
                else:
                    raise Exception("타임아웃 (최대 재시도 초과)")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    self.stdout.write(
                        f"    네트워크 오류 - 3초 후 재시도 ({attempt + 1}/{max_retries})"
                    )
                    time.sleep(3)
                    continue
                else:
                    raise Exception(f"API 요청 실패: {e}")

        return None

    def save_place(self, cid, data):
        """API 데이터를 Place 모델로 변환하여 저장"""
        traffic = data.get("traffic", {})
        extra = data.get("extra", {})

        # 좌표 파싱
        try:
            latitude = float(traffic.get("map_position_y", 0)) or None
            longitude = float(traffic.get("map_position_x", 0)) or None
        except (ValueError, TypeError):
            latitude = longitude = None

        # 일정 정보 파싱
        schedule_start = self.parse_date(data.get("schdul_info_bgnde"))
        schedule_end = self.parse_date(data.get("schdul_info_endde"))

        # API 날짜 파싱
        created_at_api = self.parse_date(data.get("creat_dt_text"))
        updated_at_api = self.parse_date(data.get("updt_dt_text"))

        Place.objects.update_or_create(
            cid=cid,
            defaults={
                "category_sn": data.get("com_ctgry_sn", ""),
                "category_path": data.get("cate_depth", ""),
                "title": data.get("post_sj", ""),
                "summary": data.get("sumry", ""),
                "description": data.get("post_desc", ""),
                "main_image": data.get("main_img", ""),
                "related_images": data.get("relate_img", []),
                "address": traffic.get("adres", ""),
                "address_new": traffic.get("new_adres", ""),
                "zip_code": traffic.get("new_zip_code", ""),
                "latitude": latitude,
                "longitude": longitude,
                "subway_info": traffic.get("subway_info", ""),
                "phone": extra.get("cmmn_telno", ""),
                "homepage": extra.get("cmmn_hmpg_url", ""),
                "opening_hours": extra.get("cmmn_use_time", ""),
                "closed_days": extra.get("closed_days", ""),
                "disabled_facilities": extra.get("disabled_facility", []),
                "tags": data.get("tag", []),
                "schedule_start": schedule_start,
                "schedule_end": schedule_end,
                "created_at_api": created_at_api,
                "updated_at_api": updated_at_api,
                "raw_data": data,
            },
        )

    def parse_date(self, date_string):
        """날짜 문자열을 date 객체로 변환"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, "%Y.%m.%d").date()
        except (ValueError, AttributeError):
            return None
