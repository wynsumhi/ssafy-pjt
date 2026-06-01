#!/bin/bash

# venv 만들기
python -m venv venv

# 가상 환경 활성화
source venv/Scripts/activate

# requirements에 있는 내용 설치하기
pip install -r requirements.txt

# ipython이 없는 경우 수동 설치
# pip install ipython

# requirements 문서 업데이트
pip freeze > requirements.txt

# 마이그레이션 실행 (필요한 경우)
python manage.py makemigrations
python manage.py migrate

# 슈퍼유저 생성 (필요한 경우)
# python manage.py createsuperuser

# 개발 서버 실행
# python manage.py runserver