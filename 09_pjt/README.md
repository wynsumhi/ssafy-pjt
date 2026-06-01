# 📚 관통PJT-09 (도서 커뮤니티 - AJAX)

## 📌 프로젝트 개요

Django와 JavaScript를 활용한 도서 커뮤니티 서비스입니다. AJAX와 비동기 통신을 활용하여 새로고침 없이 동적으로 데이터를 조회하고 조작할 수 있는 사용자 친화적인 웹 애플리케이션을 구현했습니다.

## 🛠 개발 환경

- **Language & Framework**: Python 3.11, Django 5.2, JavaScript
- **Tools**: Visual Studio Code, Chrome Browser, Git/GitLab
- **Libraries**: Bootstrap 5.3, Axios

## 📋 작업 순서

1. 요구사항 분석 및 이해
2. GitLab 프로젝트 생성 및 설정
3. 역할 분담 및 협업 방식 결정
4. 기능 구현
   - 유저 팔로우 (AJAX)
   - 쓰레드 좋아요 (AJAX)
   - 댓글 작성 및 삭제 (AJAX)
   - 도서 분류 필터링 (AJAX)
5. 테스트 및 디버깅
6. 코드 정리 및 문서화
7. GitLab 업로드 및 제출

## ✅ 요구사항 명세

### 📦 기능적 요구사항

#### 🔹 **F01 - 유저 팔로우**

- 특정 사용자를 '팔로우'할 수 있는 기능 구현
- 팔로워 수, 팔로잉 수 실시간 반영
- AJAX를 활용한 새로고침 없는 동적 UI
- 인증된 사용자만 팔로우 가능, 자기 자신은 팔로우 불가

#### 🔹 **F02 - 쓰레드 좋아요**

- 사용자가 작성한 쓰레드를 '좋아요'할 수 있는 기능 구현
- 좋아요 수 실시간 업데이트
- AJAX를 활용한 비동기 처리
- 인증된 사용자만 좋아요 가능

#### 🔹 **F03 - 댓글 작성 및 삭제**

- 사용자가 작성한 쓰레드에 댓글을 작성하고 삭제할 수 있는 기능 구현
- 댓글 작성자만 자신의 댓글 삭제 가능
- AJAX를 활용한 댓글 목록 동적 갱신
- 인증된 사용자만 댓글 작성 가능

#### 🔹 **F04 - 도서 분류 필터링**

- 특정 UI와의 상호작용에 따라 출력되는 도서 데이터가 변경되는 기능 구현
- 카테고리별 도서 필터링
- AJAX를 활용한 비동기 검색
- 사용자 인증 여부와 관계없이 동작

### 🔧 비기능적 요구사항

#### 🔹 **NF01 - Git을 활용한 프로젝트 관리**

- Commit 내역 기록 원칙 준수
- GitLab을 통한 협업 및 코드 관리

## 📂 프로젝트 구조

```
09-pjt/
├── accounts/                   # 사용자 인증 및 프로필 관리
│   ├── __pycache__/
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py               # 팔로우 기능 포함
│
├── books/                      # 도서 관리 및 커뮤니티 기능
│   ├── __pycache__/
│   ├── fixtures/              # 초기 데이터
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py              # Category, Book, Thread, Comment
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py               # AJAX 뷰 함수들
│
├── mypjt/                      # 프로젝트 설정
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── templates/                  # 전역 템플릿
│   └── base.html
│
├── .env                        # 환경 변수
├── .gitignore                  # Git 제외 파일 설정
├── db.sqlite3                  # SQLite 데이터베이스
├── manage.py                   # Django 관리 스크립트
├── README.md                   # 프로젝트 문서
└── requirements.txt            # 패키지 의존성
```

## 🎯 API 엔드포인트 설계

### RESTful API URL 구조

#### accounts 앱

| Method | Endpoint                        | 설명           | View 함수 |
| ------ | ------------------------------- | ------------ | ------- |
| GET    | `/accounts/signup/`             | 회원가입 페이지     | signup  |
| POST   | `/accounts/signup/`             | 회원가입 처리      | signup  |
| GET    | `/accounts/login/`              | 로그인 페이지      | login   |
| POST   | `/accounts/login/`              | 로그인 처리       | login   |
| POST   | `/accounts/logout/`             | 로그아웃         | logout  |
| GET    | `/accounts/profile/<username>/` | 사용자 프로필 조회   | profile |
| POST   | `/accounts/<user_pk>/follow/`   | 사용자 팔로우/언팔로우 | follow  |

#### books 앱

| Method | Endpoint                                        | 설명           | View 함수         |
| ------ | ----------------------------------------------- | ------------ | --------------- |
| GET    | `/books/`                                       | 전체 도서 목록 조회  | index           |
| GET    | `/books/filter-category/`                       | 카테고리별 도서 필터링 | filter_category |
| GET    | `/books/<book_pk>/`                             | 도서 상세 조회     | book_detail     |
| GET    | `/books/<book_pk>/thread/create/`               | 쓰레드 작성 페이지   | create_thread   |
| POST   | `/books/<book_pk>/thread/create/`               | 쓰레드 생성       | create_thread   |
| GET    | `/books/<book_pk>/thread/<thread_pk>/`          | 쓰레드 상세 조회    | thread_detail   |
| GET    | `/books/<book_pk>/thread/<thread_pk>/update/`   | 쓰레드 수정 페이지   | update_thread   |
| POST   | `/books/<book_pk>/thread/<thread_pk>/update/`   | 쓰레드 수정       | update_thread   |
| POST   | `/books/<book_pk>/thread/<thread_pk>/delete/`   | 쓰레드 삭제       | delete_thread   |
| POST   | `/books/<book_pk>/thread/<thread_pk>/likes/`    | 쓰레드 좋아요      | like            |
| POST   | `/books/<book_pk>/comment/<thread_pk>/create/`  | 댓글 생성        | create_comment  |
| DELETE | `/books/<book_pk>/comment/<comment_pk>/delete/` | 댓글 삭제        | delete_comment  |

## 🔄 Git 협업 전략

### Branch 전략

프로젝트 초기에는 기능별 브랜치 전략을 시도했으나, F03(댓글 작성 및 삭제) 기능부터는 단순한 방식으로 전환하여 진행했습니다.

**초기 Branch 구조 (F01~F02)**:

```
main
  ├── feature/follow      # F01: 유저 팔로우 기능
  └── feature/like        # F02: 쓰레드 좋아요 기능
```

**변경 후 (F03~F04)**:

- main 브랜치에서 직접 작업 진행
- 빠른 개발과 간단한 협업을 위해 브랜치 전략 단순화

### Commit 메시지 규칙

일관된 커밋 메시지 작성을 위해 다음과 같은 규칙을 수립했습니다.

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅, 세미콜론 누락 등
refactor: 코드 리팩토링
test: 테스트 코드 추가
chore: 빌드 업무 수정, 패키지 매니저 수정 등
```

**Commit 예시**:

- `feat: 팔로우 기능 구현`
- `feat: AJAX를 활용한 좋아요 기능 추가`
- `feat: 댓글 작성 및 삭제 기능 구현`
- `feat: 카테고리별 도서 필터링 기능 추가`
- `fix: 댓글 삭제 시 권한 확인 로직 수정`
- `refactor: 필터링 함수 코드 간소화`
- `docs: README 작성`

### 협업 방식

- GitLab을 통한 코드 공유 및 버전 관리
- 정기적인 커밋을 통해 작업 내역 기록
- 팀원 간 소통을 통한 역할 분담 및 진행 상황 공유
- 충돌 발생 시 직접 소통하여 해결
- 프로젝트 중반부터는 브랜치 전략을 단순화하여 개발 속도 향상

## 💡 주요 구현 내용

### 1. AJAX 비동기 통신 구현

#### Axios를 활용한 비동기 요청

모든 비동기 요청은 Axios 라이브러리를 활용하여 구현했습니다. Django의 CSRF 보호 기능과 함께 안전하게 동작하도록 설정했습니다.

```javascript
// CSRF 토큰 가져오기
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// 팔로우 기능 예시
const followBtn = document.querySelector('#follow-btn');
followBtn.addEventListener('click', function(event) {
  const userId = event.target.dataset.userId;

  axios({
    method: 'post',
    url: `/accounts/${userId}/follow/`,
    headers: {
      'X-CSRFToken': csrftoken,
    }
  })
  .then(response => {
    // 팔로워/팔로잉 수 업데이트
    document.querySelector('#followers-count').textContent = response.data.followers_count;
    document.querySelector('#followings-count').textContent = response.data.followings_count;

    // 버튼 텍스트 변경
    event.target.textContent = response.data.is_followed ? '언팔로우' : '팔로우';
  })
  .catch(error => {
    console.error('Error:', error);
  });
});
```

#### Django View에서 JSON 응답 반환

Django에서는 `JsonResponse`를 활용하여 클라이언트에게 JSON 형태의 데이터를 반환합니다.

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def follow(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)

    if request.user == user:
        return JsonResponse({'error': '자기 자신을 팔로우할 수 없습니다.'}, status=400)

    if request.user in user.followers.all():
        user.followers.remove(request.user)
        is_followed = False
    else:
        user.followers.add(request.user)
        is_followed = True

    return JsonResponse({
        'is_followed': is_followed,
        'followers_count': user.followers.count(),
        'followings_count': user.followings.count(),
    })
```

### 2. N:M 관계 구현

#### User 모델 확장

Django의 AbstractUser를 상속받아 팔로우 기능을 위한 N:M 관계를 추가했습니다.

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    followings = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers'
    )
```

- `symmetrical=False`: A가 B를 팔로우한다고 해서 B가 A를 팔로우하는 것은 아님
- `related_name='followers'`: 역참조 시 사용할 이름 지정

#### Thread-User 좋아요 관계

쓰레드와 사용자 간의 좋아요 관계를 N:M으로 구현했습니다.

```python
class Thread(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    read_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='like_threads'
    )
```

### 3. 도서 필터링 로직

카테고리별 도서 필터링을 구현하여 사용자가 원하는 장르의 도서만 조회할 수 있도록 했습니다.

```python
from django.http import JsonResponse

def filter_category(request):
    category_id = request.GET.get('category_id')

    if category_id == 'all':
        books = Book.objects.all()
    else:
        books = Book.objects.filter(category_id=category_id)

    books_data = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'cover': book.cover.url if book.cover else None,
    } for book in books]

    return JsonResponse({'books': books_data})
```

**JavaScript 구현**:

```javascript
const categoryBtns = document.querySelectorAll('.category-btn');

categoryBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    const categoryId = this.dataset.categoryId;

    axios({
      method: 'get',
      url: '/books/filter-category/',
      params: {
        category_id: categoryId
      }
    })
    .then(response => {
      const bookList = document.querySelector('#book-list');
      bookList.innerHTML = '';

      response.data.books.forEach(book => {
        const bookCard = `
          <div class="book-card">
            <img src="${book.cover}" alt="${book.title}">
            <h3>${book.title}</h3>
            <p>${book.author}</p>
            <a href="/books/${book.id}/">상세보기</a>
          </div>
        `;
        bookList.innerHTML += bookCard;
      });
    });
  });
});
```

### 4. 댓글 비동기 처리

댓글 작성 및 삭제 시 페이지 새로고침 없이 댓글 목록이 갱신되도록 구현했습니다.

```javascript
// 댓글 작성
const commentForm = document.querySelector('#comment-form');
commentForm.addEventListener('submit', function(event) {
  event.preventDefault();

  const content = document.querySelector('#comment-content').value;
  const threadId = this.dataset.threadId;
  const bookId = this.dataset.bookId;

  axios({
    method: 'post',
    url: `/books/${bookId}/comment/${threadId}/create/`,
    headers: {
      'X-CSRFToken': csrftoken,
    },
    data: {
      content: content
    }
  })
  .then(response => {
    // 댓글 목록에 새 댓글 추가
    const commentList = document.querySelector('#comment-list');
    const newComment = document.createElement('div');
    newComment.className = 'comment-item';
    newComment.innerHTML = `
      <p><strong>${response.data.username}</strong>: ${response.data.content}</p>
      <small>${response.data.created_at}</small>
      <button class="delete-btn" data-comment-id="${response.data.comment_id}">삭제</button>
    `;
    commentList.appendChild(newComment);

    // 입력 폼 초기화
    document.querySelector('#comment-content').value = '';
  })
  .catch(error => {
    alert('댓글 작성에 실패했습니다.');
  });
});

// 댓글 삭제
document.addEventListener('click', function(event) {
  if (event.target.classList.contains('delete-btn')) {
    const commentId = event.target.dataset.commentId;
    const bookId = document.querySelector('#comment-form').dataset.bookId;

    if (confirm('댓글을 삭제하시겠습니까?')) {
      axios({
        method: 'delete',
        url: `/books/${bookId}/comment/${commentId}/delete/`,
        headers: {
          'X-CSRFToken': csrftoken,
        }
      })
      .then(response => {
        // 해당 댓글 요소 제거
        event.target.closest('.comment-item').remove();
      })
      .catch(error => {
        alert('댓글 삭제에 실패했습니다.');
      });
    }
  }
});
```

### 5. 좋아요 기능

```javascript
const likeBtn = document.querySelector('#like-btn');
likeBtn.addEventListener('click', function() {
  const threadId = this.dataset.threadId;
  const bookId = this.dataset.bookId;

  axios({
    method: 'post',
    url: `/books/${bookId}/thread/${threadId}/likes/`,
    headers: {
      'X-CSRFToken': csrftoken,
    }
  })
  .then(response => {
    // 좋아요 수 업데이트
    document.querySelector('#like-count').textContent = response.data.like_count;

    // 버튼 텍스트 변경
    this.textContent = response.data.is_liked ? '좋아요 취소' : '좋아요';
  })
  .catch(error => {
    console.error('Error:', error);
  });
});
```

## 🧠 느낀 점

### Git 협업과 유연한 전략 변경

이번 프로젝트를 통해 Git을 활용한 협업의 중요성을 실감했습니다. 초반에는 기능별 브랜치 전략(feature/follow, feature/like)을 시도했으나, 프로젝트 규모와 팀 상황을 고려하여 F03부터는 main 브랜치에서 직접 작업하는 방식으로 전환했습니다.

이 과정에서 **"완벽한 프로세스보다 상황에 맞는 유연한 접근"**이 더 중요하다는 것을 배웠습니다. 브랜치 전략을 포기한 것이 아니라, 팀의 상황과 프로젝트 일정에 맞춰 효율적인 방법을 선택한 것이었습니다.

Commit 규칙은 끝까지 일관성 있게 유지하여 작업 내역을 명확히 추적할 수 있었고, 이것만으로도 충분히 효과적인 협업이 가능했습니다.

### AJAX와 비동기 통신

AJAX를 활용하면서 사용자 경험이 얼마나 개선되는지 직접 확인할 수 있었습니다. 새로고침 없이 팔로우, 좋아요, 댓글 기능이 동작하는 것을 구현하면서 현대 웹 애플리케이션의 핵심 기술을 이해하게 되었습니다.

**어려웠던 점**:

- **CSRF 토큰 처리**: Django의 보안 기능 때문에 처음에는 403 에러가 발생했습니다. CSRF 토큰을 JavaScript에서 가져와 Axios 요청 헤더에 포함시키는 방법을 학습하여 해결했습니다.
- **JSON 응답 데이터 파싱 및 DOM 조작**: JavaScript로 동적으로 HTML을 생성하고 조작하는 부분이 처음에는 어색했습니다. `innerHTML`과 `createElement`의 차이를 이해하고 적절히 활용하는 방법을 배웠습니다.
- **비동기 요청 시 발생하는 에러 핸들링**: Promise와 then/catch 구조를 이해하는데 시간이 걸렸습니다. 에러 상황에 대한 적절한 사용자 피드백을 제공하는 것이 중요함을 배웠습니다.

**해결 방법**:

- Django 공식 문서와 Axios 문서를 참고하여 CSRF 토큰을 헤더에 포함시키는 방법을 학습했습니다.
- 개발자 도구의 네트워크 탭을 활용하여 요청과 응답을 확인하며 디버깅했습니다.
- `console.log`를 적극 활용하여 데이터의 흐름을 추적하고 문제를 해결했습니다.

### N:M 관계의 이해

User 팔로우 기능과 Thread 좋아요 기능을 구현하면서 N:M 관계에 대한 이해도가 크게 높아졌습니다. `symmetrical=False` 옵션의 의미와 `related_name`의 중요성을 실감했고, Django ORM을 활용한 관계 설정과 조회가 얼마나 편리한지 알게 되었습니다.

특히 팔로우 관계에서 대칭이 아닌 관계(`symmetrical=False`)를 설정함으로써 일방향 팔로우 시스템을 구현할 수 있었고, `followers`와 `followings`라는 명확한 이름으로 양방향 조회가 가능해진 점이 인상적이었습니다.

### JavaScript와 Django의 연동

JavaScript에서 Django로 데이터를 전송하고, Django에서 처리한 결과를 다시 JavaScript로 받아 화면을 업데이트하는 전체 흐름을 이해하게 되었습니다. 특히 JSON 형태의 데이터 교환이 얼마나 효율적인지 체감했습니다.

클라이언트와 서버의 역할 분리가 명확해지면서, RESTful API의 개념도 자연스럽게 이해할 수 있었습니다.

### 사용자 경험의 중요성

페이지 새로고침 없이 데이터가 업데이트되는 것을 직접 구현하면서, 사용자 경험(UX)의 중요성을 체감했습니다. 작은 기능이지만 사용자가 느끼는 편의성은 크게 달라진다는 것을 알게 되었습니다.

### 앞으로의 목표

이번 프로젝트에서는 기본적인 AJAX CRUD 기능을 구현했지만, 실무에서는 더 복잡한 상태 관리와 에러 처리가 필요합니다. 앞으로는 다음과 같은 내용을 학습하고 적용해보고 싶습니다:

- **프론트엔드 프레임워크**: Vue.js, React를 학습하여 더 효율적인 상태 관리와 컴포넌트 기반 개발을 경험해보고 싶습니다.
- **RESTful API 설계**: API 설계 원칙을 더 깊이 학습하여 확장 가능한 API를 설계하고 싶습니다.
- **실시간 통신**: WebSocket을 활용한 실시간 알림 기능을 구현해보고 싶습니다.
- **성능 최적화**: 페이지네이션, 무한 스크롤, 이미지 Lazy Loading 등을 통해 성능을 최적화하는 방법을 학습하고 싶습니다.
- **테스트 코드 작성**: 단위 테스트와 통합 테스트를 작성하여 안정적인 코드를 작성하는 습관을 기르고 싶습니다.

### 협업을 통한 성장

팀원과 함께 요구사항을 분석하고, 역할을 분담하며, 문제를 해결해 나가는 과정에서 많은 것을 배웠습니다. 특히 서로의 코드를 공유하고 개선 방안을 논의하면서 더 나은 코드를 작성하는 방법을 익힐 수 있었습니다.

혼자서는 발견하지 못했을 버그를 팀원이 발견해주거나, 더 효율적인 로직을 제안받는 경험을 통해 협업의 가치를 실감했습니다.

## 🔗 참고 자료

- [Django Documentation](https://www.djangoproject.com/start/overview/)
- [MDN Web Docs - AJAX](https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX)
- [Axios Documentation](https://axios-http.com/)
- [Bootstrap 5.3](https://getbootstrap.com/)
- [Django JsonResponse](https://docs.djangoproject.com/en/5.2/ref/request-response/#jsonresponse-objects)

---

**프로젝트 기간**: 2025.11.28  
**사용 기술**: Django 5.2, JavaScript, Axios, Bootstrap 5.3  
**프로젝트 명**: 09-pjt
