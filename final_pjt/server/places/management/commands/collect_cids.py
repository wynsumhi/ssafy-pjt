# server/places/management/commands/collect_cids.py
import os
import time

from django.core.management.base import BaseCommand

import requests

from places.models import PlaceCID


class Command(BaseCommand):
    help = "Visit Seoul API에서 모든 CID 수집"

    API_BASE_URL = "https://api-call.visitseoul.net/api/v1/contents/list"
    API_KEY = os.getenv("VISIT_SEOUL_API_KEY")

    # 수집할 카테고리 목록 (필요에 따라 추가)
    CATEGORIES = [
        "Ca0o2d4",  # Culture-L1
        # "Ce9z7g9",  # Parks
        # "Ca1u7i6",  # Cultural Districts
        # "Cr1f0k2",  # Performance Halls
        # "Cl5y4k0",  # Landmarks
        # "Ct4h4b7",  # Other Cultural Destinations
        # "Co0g3x0",  # Leisure/Sports Centers
        # "Cl2d2s1",  # Education Centers
        # "Cy5h2x9",  # Theme Parks
        # "Cp7e6o3",  # Convention Centers
        # "Cg1x6l1",  # Cultural Facilities
        # "Cy6j7j7",  # Others Cultural Facilities
        # "Ct9t6m8",  # Art Museums/Galleries
        # "Cr0q2v2",  # Museums
        "Cu8e6t5",  # Shopping-L1
        # "Cn0t1e0",  # Specialty Shops & Stores
        # "Cy4k5t1",  # Shopping Malls & Outlets
        # "Cn7z1h7",  # Traditional Markets
        # "Cs3j7y4",  # Department Stores
        # "Cp5i3g2",  # Duty Free Shops
        # "Ct1z4k9",  # Supermarkets & Warehouses
        "Ch4v8z7",  # Accommodations-L1
        # "Ce7q5s7",  # Hotels
        # "Ct9n1n3",  # Hostels
        "Ca1z6p7",  # History-L1
        # "Cw1i3e4",  # Religious Sites
        # "Cl1k5b1",  # Historical Sites
        # "Ch5t7s7",  # Palaces
        # "Cb9c5i3",  # Tombs & Mausoleums
        # "Ci7i9i6",  # Modern Architecture
        # "Cr6m1i5",  # Others Historical Sites
        # "Cb9o5c4",  # Historical Sites
        # "Co2n1h7",  # Fortresses & Gates
        "Cl9s3y9",  # Cuisine-L1
        # "Cz9d1h6",  # Korean Restaurants
        # "Cx0t8m5",  # Cafes & Tea Shops
        # "Ck6n0w6",  # Bars & Clubs
        # "Cx2j0n1",  # Foreign Restaurant
        # "Cn7k2s5",  # Others
        # "Cl9n1c2",  # Western
        # "Ch7l5i4",  # Japanese
        # "Cm1y8v1",  # Chinese
        # "Cx3e9k9",  # Fusion
        "Co6c2n2",  # Nature-L1
        # "Cu5u8d4",  # Natural Sites(Mountains)
        # "Cw8j0y7",  # Natural Sites(Rivers)
        # "Cp3b3j9",  # Natural Sites(Parks)
        "Cc9i5o2",  # Experience Programs-L1
        # "Cr6o1h2",  # Industrial Sites
        # "Cq3m6s6",  # Craft Workshops
        # "Cd0m9o0",  # Traditional Experience
        # "Cl8f8q1",  # Other Experiences
        # "Cf1y9k1",  # Wellness
        # "Cq9d5v0",  # Temple Stays
        "Cv7s8m5",  # Festivals/Events/Performances-L1
        # "Cd4y5u1",  # Festivals
        # "Cb2b0t2",  # Performances
        # "Cf9q1q4",  # Events
        # "Cw7q1x8",  # Other Events
        # "Cu6j1f4",  # Expos
        # "Cu9u5z7",  # Exhibitions
    ]

    def add_arguments(self, parser):
        parser.add_argument("--category", type=str, help="특정 카테고리만 수집")

    def handle(self, *args, **options):
        if not self.API_KEY:
            self.stdout.write(self.style.ERROR("VISIT_SEOUL_API_KEY가 설정되지 않았습니다."))
            return

        categories = [options["category"]] if options["category"] else self.CATEGORIES

        total_collected = 0
        for category in categories:
            count = self.collect_category(category)
            total_collected += count
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS(f"총 {total_collected}개 CID 수집 완료"))

    def collect_category(self, category_sn):
        page_no = 1
        collected = 0

        self.stdout.write(f"\n{category_sn} 카테고리 수집 시작...")

        while True:
            data = self.fetch_page(category_sn, page_no)

            if not data or not data.get("data"):
                break

            # CID 저장
            for item in data["data"]:
                PlaceCID.objects.update_or_create(
                    cid=item["cid"],
                    defaults={
                        "category_sn": item.get("com_ctgry_sn", ""),
                        "category_path": item.get("cate_depth", ""),
                        "title": item.get("post_sj", ""),
                        "summary": item.get("sumry", ""),
                        "main_image": item.get("main_img", ""),
                    },
                )
                collected += 1

            # 페이징 체크
            paging = data.get("paging", {})
            total_count = paging.get("total_count", 0)
            page_size = paging.get("page_size", 50)

            self.stdout.write(
                f'  페이지 {page_no}: {len(data["data"])}개 수집 (전체: {total_count})'
            )

            if page_no * page_size >= total_count:
                break

            page_no += 1
            time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS(f"{category_sn}: {collected}개 수집 완료"))
        return collected

    def fetch_page(self, category_sn, page_no):
        try:
            response = requests.post(
                self.API_BASE_URL,
                headers={
                    "VISITSEOUL-API-KEY": self.API_KEY,
                    "Accept": "application/json;charset=UTF-8",
                    "Content-Type": "application/json;charset=UTF-8",
                },
                json={
                    "com_ctgry_sn": category_sn,
                    "lang_code_id": "ko",
                    "sort_type": "latest",
                    "page_no": page_no,
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API 요청 실패: {e}"))
            return None
