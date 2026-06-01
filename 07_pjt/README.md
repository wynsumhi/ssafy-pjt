# 📚 관통PJT-07 (도서)

## 📌 프로젝트 개요

- 도서 관련 데이터를 제공하는 RESTful API 서버를 구축하는 프로젝트입니다. Django REST Framework를 활용하여 도서, 카테고리, 게시글, 댓글 데이터의 조회가 가능하며, 사용자가 게시글을 남기고 관리할 수 있는 API를 제공합니다.




## 🛠 개발 환경

- Language & Framework: Python 3.11, Django 5.2, Django REST Framework
- Tools: Postman (API 테스트), SQLite
- IDE: Visual Studio Code, Git/GitLab, Postman



## 👥 팀원

- 강민규
- 김현아



## 📋 작업 순서

1. 요구사항 분석 및 이해

2. GitLab 프로젝트 생성 및 설정

3. 역할 분담 및 협업 방식 결정

4.  기능 구현
   
   - 프로젝트 및 앱 구성
   
   - Model 설계 및 구현
   
   - Serializer 작성
   
   - API View 함수 구현
   
   - URL 설계 (RESTful)

5. Postman 테스트

6. 코드 정리 및 문서화

7. GitLab 업로드 및 제출



## ✅ 요구사항 명세

### 📦 기능적 요구사항

🔹 **F01 - 프로젝트 구성**

- 도서 커뮤니티 서비스의 API 서버 구현을 위한 Django 프로젝트 및 앱 생성
- 프로젝트 이름: mypjt
- 앱 이름: books

---

🔹 **F02 - Category Model 클래스**

- 카테고리 데이터를 데이터베이스에 저장할 수 있도록 Django Model 클래스 구현
- 카테고리 이름을 저장할 필드 구성

---

🔹 **F03 - Book Model 클래스**

- 도서 데이터를 데이터베이스에 저장할 수 있도록 Django Model 클래스 구현
- 도서 제목, 설명, ISBN, 커버 이미지, 출판사, 출간일, 저자명, 회원 리뷰 평점 등 필드 구성
- Category와 N:1 관계 설정

---

🔹 **F04 - Thread Model 클래스**

- 게시글 데이터를 데이터베이스에 저장할 수 있도록 Django Model 클래스 구현
- 게시글 제목, 본문, 독서일, 생성 시각, 수정 시각 필드 구성
- Book과 N:1 관계 설정

---

🔹 **F05 - Comment Model 클래스**

- 게시글 댓글 데이터를 데이터베이스에 저장할 수 있도록 Django Model 클래스 구현
- 댓글 내용, 생성 시각, 수정 시각 필드 구성
- Thread와 N:1 관계 설정

---

🔹 **F06 - Serializer 클래스**

- 사용자의 입력 데이터 검증 및 응답 데이터 형식을 위한 Serializer 클래스를 개별 요구사항에 맞춰서 구현
- Django REST Framework의 ModelSerializer 활용
- 각 Model에 대한 적절한 Serializer 작성

---

🔹 **F07 - category_list (전체 카테고리 데이터 조회)**

- 전체 카테고리 데이터를 조회하는 view 함수 구현
- GET method에 대해서만 동작
- 각 카테고리의 id, 이름 데이터 조회

---

🔹 **F08 - book_list (전체 도서 데이터 조회)**

- 전체 도서 데이터를 조회하는 view 함수 구현
- GET method에 대해서만 동작
- 각 도서의 id, 제목, 작가, isbn, 커버 이미지 데이터 조회

---

🔹 **F09 - book_detail (단일 도서 데이터 조회)**

- 단일 도서 데이터를 조회하는 view 함수 구현
- GET method에 대해서만 동작
- 대상 도서의 데이터와 함께, 도서의 카테고리, 게시글 목록, 총 게시글 개수 정보 함께 조회
- 조회되는 게시글: id, 제목, 내용, 독서일 데이터

---

🔹 **F10 - thread_list (전체 게시글 데이터 조회)**

- 전체 게시글 데이터를 조회하는 view 함수 구현
- GET method에 대해서만 동작
- 각 게시글의 id, 제목과 함께, 대상 도서의 제목이 함께 조회

---

🔹 **F11 - thread_detail (단일 게시글 데이터 조회, 수정, 삭제)**

- 단일 게시글 데이터를 조회, 수정, 삭제하는 view 함수 구현
- **GET method**: 해당 게시글 데이터와 함께, 대상 도서, 댓글 목록, 댓글 개수 정보 조회
- **PUT method**: 유효한 데이터인 경우 대상 게시글 수정
- **DELETE method**: 대상 게시글 삭제

---

🔹 **F12 - create_thread (게시글 데이터 저장)**

- 전달받은 게시글 데이터를 데이터베이스에 저장하는 view 함수 구현
- POST method에 대해서만 동작
- 제목, 내용, 독서일 데이터를 전달받아 새로운 게시글 생성
- 유효한 데이터인 경우에만 정상 작동

---

🔹 **F13 - create_comment (게시글 댓글 데이터 저장)**

- 전달받은 게시글 댓글 데이터를 데이터베이스에 저장하는 view 함수 구현
- POST method에 대해서만 동작
- 내용 데이터를 전달받아 새로운 댓글 생성
- 대상이 되는 게시글은 RESTful 설계 원칙을 고려하여 판별
- 유효한 데이터인 경우에만 정상 작동

---

🔹 **F14 - comment_detail (단일 게시글 댓글 데이터 조회, 수정, 삭제)**

- 단일 게시글 댓글 데이터를 조회, 수정, 삭제하는 view 함수 구현
- **GET method**: 해당 댓글 데이터와 함께, 대상 게시글의 제목이 함께 조회
- **PUT method**: 유효한 데이터인 경우 대상 댓글 수정
- **DELETE method**: 대상 댓글 삭제



## 📂 프로젝트 구조

```
07-pjt/
├── books/                      # 도서 관리 API 앱
│   ├── migrations/
│   ├── fixtures/              # 초기 데이터
│   │   ├── books.json
│   │   ├── categories.json
│   │   ├── threads.json
│   │   └── comments.json
│   ├── models.py              # Category, Book, Thread, Comment 모델
│   ├── serializers.py         # DRF Serializers
│   ├── views.py               # API View 함수들
│   └── urls.py                # API URL 패턴
├── mypjt/                     # 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .gitignore
├── db.sqlite3S
├── manage.py
├── requirements.txt
└── README.md
```

#### 🎯 API 엔드포인트 설계

#### RESTful API URL 구조

| Method | Endpoint                                 | 설명            | View 함수        |
| ------ | ---------------------------------------- | ------------- | -------------- |
| GET    | `/books/categories/`                       | 전체 카테고리 목록 조회 | category_list  |
| GET    | `/books/`                            | 전체 도서 목록 조회   | book_list      |
| GET    | `/books/<int:book_pk>/`                   | 단일 도서 상세 조회   | book_detail    |
| GET    | `/books/threads/`                          | 전체 게시글 목록 조회  | thread_list    |
| GET    | `/books/threads/<int:thread_pk>/`                 | 게시글 상세 조회     | thread_detail  |
| PUT    | `/books/threads/<int:thread_pk>/`                 | 게시글 수정        | thread_detail  |
| DELETE | `/books/threads/<int:thread_pk>/`                 | 게시글 삭제        | thread_detail  |
| POST   | `/books/<int:book_pk>/threads/create/`      | 게시글 생성        | create_thread  |
| POST   | `/books/threads/<int:thread_pk>/comments/` | 댓글 생성         | create_comment |
| GET    | `/books/comments/<int:comment_pk>/`                | 댓글 상세 조회      | comment_detail |
| PUT    | `/books/comments/<int:comment_pk>/`                | 댓글 수정         | comment_detail |
| DELETE | `/books/comments/<int:comment_pk>/`                | 댓글 삭제         | comment_detail |





## 🧠 느낀 점

Git을 활용한 협업 과정에서 Branch 전략과 Commit 규칙의 중요성을 실감했습니다. 실제 협업 과정을 통해 프로젝트 세팅 및 작업 진행 시 명확한 역할 분담과 소통이 프로젝트 진행에 얼마나 큰 영향을 미치는지 깨달았습니다. Merge Conflict를 해결하면서 코드 리뷰의 필요성도 느꼈습니다.

### 기술적 성장

이번 프로젝트를 통해 Django REST Framework를 활용한 RESTful API 서버 구축 경험을 쌓을 수 있었습니다. 특히 Serializer의 강력함과 @api_view 데코레이터의 편리함을 체감했으며, RESTful 설계 원칙의 중요성을 깨달았습니다.

### API 설계의 중요성

좋은 API는 직관적이고 일관성 있어야 한다는 것을 배웠습니다. URL 구조, HTTP Method 선택, Status Code 사용 등 모든 것이 API 사용성에 영향을 미친다는 것을 실감했습니다.

### Postman을 통한 테스트

API 개발에서 테스트의 중요성을 배웠습니다. Postman을 활용하여 각 엔드포인트를 체계적으로 테스트하면서, 예외 상황에 대한 처리와 에러 메시지의 중요성도 깨달았습니다.

### 협업과 문서화

API는 프론트엔드 개발자와의 협업에서 계약서 같은 역할을 합니다. 명확한 API 명세서 작성과 일관된 응답 형식이 얼마나 중요한지 알게 되었습니다.

### 앞으로의 목표

이번 프로젝트는 기본적인 CRUD API 구현이었지만, 실제 서비스를 위해서는 인증, 권한, 페이지네이션, 검색 등 더 많은 기능이 필요합니다. 앞으로는 이런 실무 기능들을 추가로 학습하고, 프론트엔드와 연동하는 풀스택 프로젝트를 진행해보고 싶습니다.
