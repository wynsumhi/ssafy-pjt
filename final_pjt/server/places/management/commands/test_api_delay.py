# server/places/management/commands/test_api_delay.py
import os
import time

from django.core.management.base import BaseCommand

import requests

from places.models import PlaceCID


class Command(BaseCommand):
    help = "API 요청 간격 최적화 테스트"

    API_BASE_URL = "https://api-call.visitseoul.net/api/v1/contents/info"
    API_KEY = os.getenv("VISIT_SEOUL_API_KEY")

    def add_arguments(self, parser):
        parser.add_argument("--start-delay", type=float, default=0.5, help="시작 딜레이 (초)")
        parser.add_argument("--end-delay", type=float, default=3.0, help="종료 딜레이 (초)")
        parser.add_argument("--step", type=float, default=0.1, help="딜레이 증가 단위 (초)")
        parser.add_argument(
            "--requests-per-test", type=int, default=20, help="각 딜레이당 테스트할 요청 수"
        )

    def handle(self, *args, **options):
        if not self.API_KEY:
            self.stdout.write(self.style.ERROR("VISIT_SEOUL_API_KEY가 설정되지 않았습니다."))
            return

        start_delay = options["start_delay"]
        end_delay = options["end_delay"]
        step = options["step"]
        requests_per_test = options["requests_per_test"]

        # 테스트용 CID 목록 (미수집 CID에서 가져오기)
        test_cids = list(
            PlaceCID.objects.filter(is_fetched=False).values_list("cid", flat=True)[
                : requests_per_test * 20
            ]  # 여유있게 가져오기
        )

        if len(test_cids) < requests_per_test:
            self.stdout.write(
                self.style.ERROR(f"테스트할 CID가 부족합니다. 최소 {requests_per_test}개 필요")
            )
            return

        self.stdout.write("=" * 70)
        self.stdout.write("API 딜레이 최적화 테스트 시작")
        self.stdout.write("=" * 70)
        self.stdout.write(f"테스트 범위: {start_delay}초 ~ {end_delay}초 (간격: {step}초)")
        self.stdout.write(f"각 딜레이당 요청 수: {requests_per_test}개")
        self.stdout.write("=" * 70 + "\n")

        results = []
        current_delay = start_delay
        cid_index = 0

        while current_delay <= end_delay:
            self.stdout.write(f"\n📊 테스트 {len(results) + 1}: 딜레이 {current_delay:.2f}초")
            self.stdout.write("-" * 70)

            success_count = 0
            error_count = 0
            error_types = {}
            total_time = 0

            test_start_time = time.time()

            for i in range(requests_per_test):
                if cid_index >= len(test_cids):
                    self.stdout.write(self.style.WARNING("테스트용 CID 소진"))
                    break

                cid = test_cids[cid_index]
                cid_index += 1

                request_start = time.time()

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

                    request_time = time.time() - request_start
                    total_time += request_time

                    if response.status_code == 200:
                        success_count += 1
                        self.stdout.write(
                            f"  [{i+1}/{requests_per_test}] ✅ 성공 ({request_time:.2f}초)",
                            ending="",
                        )
                    elif response.status_code == 500:
                        error_count += 1
                        error_types["500_Server_Error"] = error_types.get("500_Server_Error", 0) + 1
                        self.stdout.write(f"  [{i+1}/{requests_per_test}] ❌ 500 에러", ending="")
                    else:
                        error_count += 1
                        error_types[f"HTTP_{response.status_code}"] = (
                            error_types.get(f"HTTP_{response.status_code}", 0) + 1
                        )
                        self.stdout.write(
                            f"  [{i+1}/{requests_per_test}] ❌ {response.status_code}", ending=""
                        )

                except requests.exceptions.Timeout:
                    error_count += 1
                    error_types["Timeout"] = error_types.get("Timeout", 0) + 1
                    self.stdout.write(f"  [{i+1}/{requests_per_test}] ⏱️ 타임아웃", ending="")

                except Exception as e:
                    error_count += 1
                    error_types["기타"] = error_types.get("기타", 0) + 1
                    self.stdout.write(
                        f"  [{i+1}/{requests_per_test}] ⚠️ 오류: {str(e)[:30]}", ending=""
                    )

                # 진행상황 표시
                if (i + 1) % 5 == 0:
                    self.stdout.write("")  # 줄바꿈

                # 마지막 요청이 아니면 대기
                if i < requests_per_test - 1:
                    time.sleep(current_delay)

            test_total_time = time.time() - test_start_time
            avg_request_time = total_time / requests_per_test if requests_per_test > 0 else 0
            success_rate = (success_count / requests_per_test * 100) if requests_per_test > 0 else 0

            # 결과 저장
            result = {
                "delay": current_delay,
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": success_rate,
                "avg_request_time": avg_request_time,
                "total_time": test_total_time,
                "error_types": error_types,
            }
            results.append(result)

            # 결과 출력
            self.stdout.write("\n" + "-" * 70)
            self.stdout.write(
                f"결과: 성공 {success_count}/{requests_per_test} ({success_rate:.1f}%)"
            )
            self.stdout.write(f"평균 응답시간: {avg_request_time:.2f}초")
            self.stdout.write(f"총 소요시간: {test_total_time:.1f}초")

            if error_types:
                self.stdout.write("오류 유형:")
                for error_type, count in error_types.items():
                    self.stdout.write(f"  - {error_type}: {count}개")

            # 성공률이 95% 이상이면 최적 딜레이로 판단
            if success_rate >= 95.0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n🎯 최적 딜레이 발견: {current_delay:.2f}초 (성공률 {success_rate:.1f}%)"
                    )
                )
                break

            current_delay += step

        # 최종 결과 요약
        self.stdout.write("\n\n" + "=" * 70)
        self.stdout.write("📈 테스트 결과 요약")
        self.stdout.write("=" * 70)

        # 표 형식으로 출력
        self.stdout.write(
            f"{'딜레이':>8} | {'성공률':>8} | {'성공':>6} | {'실패':>6} | {'평균응답':>10} | {'총시간':>10}"
        )
        self.stdout.write("-" * 70)

        for result in results:
            self.stdout.write(
                f"{result['delay']:>7.2f}초 | "
                f"{result['success_rate']:>7.1f}% | "
                f"{result['success_count']:>6}개 | "
                f"{result['error_count']:>6}개 | "
                f"{result['avg_request_time']:>9.2f}초 | "
                f"{result['total_time']:>9.1f}초"
            )

        # 권장 딜레이
        self.stdout.write("\n" + "=" * 70)

        successful_delays = [r for r in results if r["success_rate"] >= 95.0]

        if successful_delays:
            optimal = min(successful_delays, key=lambda x: x["delay"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ 권장 딜레이: {optimal['delay']:.2f}초 (성공률 {optimal['success_rate']:.1f}%)"
                )
            )

            # 3560개 수집 시 예상 시간
            estimated_time = 3560 * optimal["delay"] / 60  # 분 단위
            estimated_hours = int(estimated_time // 60)
            estimated_minutes = int(estimated_time % 60)

            self.stdout.write(f"\n📅 3560개 수집 예상 시간: ", ending="")
            if estimated_hours > 0:
                self.stdout.write(f"{estimated_hours}시간 {estimated_minutes}분")
            else:
                self.stdout.write(f"{estimated_minutes}분")

        else:
            best = max(results, key=lambda x: x["success_rate"])
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ 95% 성공률 미달성. 최고 성공률: {best['delay']:.2f}초 ({best['success_rate']:.1f}%)"
                )
            )
            self.stdout.write(f"권장: {best['delay'] + 0.5:.2f}초 이상 사용")

        self.stdout.write("=" * 70)
