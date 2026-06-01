## Django PJT - README

안녕하세요, 노삼 여러분. 현재까지 진행된 **Django 프로젝트**의 상황을 공유하며, **VS Code Live Share**를 통해 코드를 함께 확인하고 논의할 수 있도록 준비했습니다. 이 문서는 **Live Share 공유 이전에 이미 설정 완료된 내용**만을 정리합니다.

[Live Share](https://prod.liveshare.vsengsaas.visualstudio.com/join?30107D7D03E972DD846F4E1FE2F9BFFE9ABF)

### 프로젝트 및 앱 이름 설정 현황

명세서에 따라 프로젝트 및 앱 이름 설정이 완료되었습니다.

- **프로젝트 이름**: `mypjt`

- **앱 이름**: `accounts`, `books`

### 커스텀 User 모델 및 초기 설정

- **커스텀 User 모델**을 설정하여, 사용자 인증과 관련된 확장에 유연하게 대비했습니다.

- 커스텀 모델 설정 후, **`migrate`** 명령을 통해 데이터베이스에 해당 변경사항을 반영하는 작업을 완료했습니다.

- **템플릿 기본 구조**: 루트 폴더의 `templates/base.html` 파일에 **Bootstrap 5 CDN**을 연결하여 모든 페이지에서 일관된 스타일링 환경을 구축했습니다.

### 개발 환경 설정 가이드 및 공유 파일

첨부된 `run_commands.sh` 파일을 이용하여 개발 환경을 쉽게 설정할 수 있습니다.

#### 1. 실행 권한 부여 및 스크립트 실행

Git Bash 등의 터미널 환경에서 스크립트 실행 권한을 부여한 후 실행합니다.

```
chmod +x run_commands.sh./run_commands.sh
```

#### `run_commands.sh` 내용

스크립트 내용은 가상 환경 설정, 라이브러리 설치, 마이그레이션을 자동화합니다.

```
#!/bin/bash# venv 만들기python -m venv venv# 가상 환경 활성화source venv/Scripts/activate# requirements에 있는 내용 설치하기pip install -r requirements.txt# requirements 문서 업데이트pip freeze > requirements.txt# 마이그레이션 실행python manage.py makemigrationspython manage.py migrate# 개발 서버 실행# python manage.py runserver 
```

#### 2. 공유 파일 목록

프로젝트 환경 관리를 위해 아래 두 파일도 함께 공유합니다.

- **`requirements.txt`**: 프로젝트에 필요한 Python 라이브러리 목록입니다.

- **`.gitignore`**: Git으로 관리하지 않을 파일 및 폴더 목록입니다. (가상 환경 폴더 `venv`, `.sqlite3` DB 파일 등이 포함됩니다.)

### Admin 계정 정보

프로젝트 테스트 및 초기 관리를 위해 **`admin` 계정**을 설정했습니다.

| 항목           | 정보       |
| ------------ | -------- |
| **Username** | `admin`  |
| **Password** | `qwe123` |

**주의**: 이 계정은 초기 개발용이며, 보안을 위해 이후 단계에서 반드시 변경하거나 안전하게 관리해야 합니다.
