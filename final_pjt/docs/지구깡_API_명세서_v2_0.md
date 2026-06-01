# 지구깡(Jigukkang) API 명세서 v2.0

**Base URL**: `http://localhost:8000/api/v1`  
**인증 방식**: JWT Bearer Token  
**최종 수정일**: 2025-12-26

---

## 목차

1. [인증 (Authentication)](#1-인증-authentication)
2. [사용자 (Users)](#2-사용자-users)
3. [마이페이지 (MyPage)](#3-마이페이지-mypage)
4. [게시글 (Articles)](#4-게시글-articles)
5. [댓글 (Comments)](#5-댓글-comments)
6. [뽑기 (Draws)](#6-뽑기-draws)
7. [장소 (Places)](#7-장소-places)

---

## 1. 인증 (Authentication)

### 1.1 회원가입

| 항목           | 내용                             |
| ------------ | ------------------------------ |
| **Method**   | POST                           |
| **Endpoint** | `/auth/signup/`                |
| **설명**       | 새로운 사용자 계정을 생성하고 JWT 토큰을 발급합니다 |
| **인증 필요**    | 불필요                            |

**Request Body**

```json
{
  "username": "user123",
  "password": "password123!",
  "password2": "password123!",
  "nickname": "지구깡유저"
}
```

**필드 설명**

- `username`: 사용자 아이디 (필수, 고유값)
- `password`: 비밀번호 (필수, 최소 8자)
- `password2`: 비밀번호 확인 (필수)
- `nickname`: 닉네임 (필수, 고유값)

**Response (201 Created)**

```json
{
  "user": {
    "id": 1,
    "nickname": "지구깡유저",
    "profile_image": null
  },
  "message": "회원가입이 완료되었습니다.",
  "token": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Response (400 Bad Request)**

```json
{
  "username": ["이미 존재하는 사용자명입니다."],
  "password": ["비밀번호가 너무 짧습니다."],
  "nickname": ["이미 존재하는 닉네임입니다."]
}
```

---

### 1.2 로그인

| 항목           | 내용                      |
| ------------ | ----------------------- |
| **Method**   | POST                    |
| **Endpoint** | `/auth/login/`          |
| **설명**       | 사용자 인증 후 JWT 토큰을 발급받습니다 |
| **인증 필요**    | 불필요                     |

**Request Body**

```json
{
  "username": "user1",
  "password": "password123!"
}
```

**Response (200 OK)**

```json
{
  "user": {
    "id": 1,
    "nickname": "지구깡유저",
    "profile_image": "https://example.com/profile/1.jpg"
  },
  "message": "로그인 성공",
  "token": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Response (401 Unauthorized)**

```json
{
  "error": "아이디 또는 비밀번호가 올바르지 않습니다."
}
```

---

### 1.3 토큰 갱신

| 항목           | 내용                                 |
| ------------ | ---------------------------------- |
| **Method**   | POST                               |
| **Endpoint** | `/auth/token/refresh/`             |
| **설명**       | Refresh 토큰으로 새로운 Access 토큰을 발급받습니다 |
| **인증 필요**    | 불필요                                |

**Request Body**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK)**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (401 Unauthorized)**

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 1.4 로그아웃

| 항목           | 내용                             |
| ------------ | ------------------------------ |
| **Method**   | POST                           |
| **Endpoint** | `/auth/logout/`                |
| **설명**       | Refresh 토큰을 블랙리스트에 추가하여 무효화합니다 |
| **인증 필요**    | 필요                             |

**Headers**

```
Authorization: Bearer {access_token}
```

**Request Body**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK)**

```json
{
  "message": "로그아웃되었습니다."
}
```

**Response (400 Bad Request)**

```json
{
  "error": "로그아웃 처리 중 오류가 발생했습니다."
}
```

---

### 1.5 현재 사용자 정보 조회

| 항목           | 내용                     |
| ------------ | ---------------------- |
| **Method**   | GET                    |
| **Endpoint** | `/auth/user/`          |
| **설명**       | 현재 로그인한 사용자의 정보를 조회합니다 |
| **인증 필요**    | 필요                     |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (200 OK)**

```json
{
  "id": 1,
  "nickname": "지구깡유저",
  "profile_image": "https://example.com/profile/1.jpg"
}
```

---

## 2. 사용자 (Users)

### 2.1 사용자 프로필 조회

| 항목           | 내용                    |
| ------------ | --------------------- |
| **Method**   | GET                   |
| **Endpoint** | `/users/{user_id}/`   |
| **설명**       | 특정 사용자의 공개 프로필을 조회합니다 |
| **인증 필요**    | 필요                    |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (200 OK)**

```json
{
  "id": 1,
  "username": "user1",
  "nickname": "지구깡유저",
  "bio": "안녕하세요!",
  "profile_image": "https://example.com/profile/1.jpg",
  "article_count": 15,
  "follower_count": 120,
  "following_count": 85,
  "is_following": false
}
```

**Response (404 Not Found)**

```json
{
  "error": "사용자를 찾을 수 없습니다"
}
```

---

### 2.2 팔로우

| 항목           | 내용                         |
| ------------ | -------------------------- |
| **Method**   | POST                       |
| **Endpoint** | `/users/{user_id}/follow/` |
| **설명**       | 사용자를 팔로우합니다                |
| **인증 필요**    | 필요                         |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (201 Created)**

```json
{
  "message": "팔로우했습니다",
  "is_following": true,
  "follower_count": 121
}
```

**Response (400 Bad Request)**

```json
{
  "error": "이미 팔로우한 사용자입니다"
}
```

```json
{
  "error": "자기 자신을 팔로우할 수 없습니다"
}
```

---

### 2.3 언팔로우

| 항목           | 내용                         |
| ------------ | -------------------------- |
| **Method**   | DELETE                     |
| **Endpoint** | `/users/{user_id}/follow/` |
| **설명**       | 팔로우를 취소합니다                 |
| **인증 필요**    | 필요                         |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

```
(빈 응답)
```

**Response (400 Bad Request)**

```json
{
  "error": "팔로우하지 않은 사용자입니다"
}
```

---

### 2.4 팔로워 목록 조회

| 항목           | 내용                            |
| ------------ | ----------------------------- |
| **Method**   | GET                           |
| **Endpoint** | `/users/{user_id}/followers/` |
| **설명**       | 사용자의 팔로워 목록을 조회합니다            |
| **인증 필요**    | 필요                            |

**Headers**

```
Authorization: Bearer {access_token}
```

**Query Parameters**

- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지당 사용자 수 (기본: 50, 최대: 100)

**Response (200 OK)**

```json
{
  "results": [
    {
      "id": 2,
      "nickname": "팔로워1",
      "profile_image": "https://example.com/profile/2.jpg"
    },
    {
      "id": 3,
      "nickname": "팔로워2",
      "profile_image": null
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_count": 120,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### 2.5 팔로잉 목록 조회

| 항목           | 내용                            |
| ------------ | ----------------------------- |
| **Method**   | GET                           |
| **Endpoint** | `/users/{user_id}/following/` |
| **설명**       | 사용자가 팔로우하는 사람들의 목록을 조회합니다     |
| **인증 필요**    | 필요                            |

**Headers**

```
Authorization: Bearer {access_token}
```

**Query Parameters**

- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지당 사용자 수 (기본: 50, 최대: 100)

**Response (200 OK)**

```json
{
  "results": [
    {
      "id": 5,
      "nickname": "팔로잉1",
      "profile_image": "https://example.com/profile/5.jpg"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 2,
    "total_count": 85,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## 3. 마이페이지 (MyPage)

### 3.1 내 프로필 조회

| 항목           | 내용                         |
| ------------ | -------------------------- |
| **Method**   | GET                        |
| **Endpoint** | `/mypage/profile/`         |
| **설명**       | 현재 로그인한 사용자의 프로필 정보를 조회합니다 |
| **인증 필요**    | 필요                         |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (200 OK)**

```json
{
  "id": 1,
  "username": "user1",
  "nickname": "지구깡유저",
  "bio": "안녕하세요!",
  "profile_image": "https://example.com/profile/1.jpg",
  "article_count": 15,
  "follower_count": 120,
  "following_count": 85
}
```

---

### 3.2 내 프로필 수정

| 항목           | 내용                                |
| ------------ | --------------------------------- |
| **Method**   | PATCH                             |
| **Endpoint** | `/mypage/profile/`                |
| **설명**       | 프로필 정보를 수정합니다 (닉네임, 프로필 이미지, 소개글) |
| **인증 필요**    | 필요                                |

**Headers**

```
Authorization: Bearer {access_token}
```

**Request Body**

```json
{
  "nickname": "새로운닉네임",
  "bio": "새로운 소개글입니다.",
  "profile_image": "https://example.com/new-profile.jpg"
}
```

**필드 설명**

- `nickname`: 닉네임 (선택, 고유값)
- `bio`: 소개글 (선택)
- `profile_image`: 프로필 이미지 URL (선택)

**Response (200 OK)**

```json
{
  "id": 1,
  "username": "user1",
  "nickname": "새로운닉네임",
  "bio": "새로운 소개글입니다.",
  "profile_image": "https://example.com/new-profile.jpg",
  "article_count": 15,
  "follower_count": 120,
  "following_count": 85
}
```

**Response (400 Bad Request)**

```json
{
  "nickname": ["이미 존재하는 닉네임입니다."]
}
```

---

### 3.3 비밀번호 변경

| 항목           | 내용                             |
| ------------ | ------------------------------ |
| **Method**   | POST                           |
| **Endpoint** | `/mypage/password/`            |
| **설명**       | 현재 비밀번호를 확인한 후 새로운 비밀번호로 변경합니다 |
| **인증 필요**    | 필요                             |

**Headers**

```
Authorization: Bearer {access_token}
```

**Request Body**

```json
{
  "current_password": "oldpassword123!",
  "new_password": "newpassword456!",
  "new_password_confirm": "newpassword456!"
}
```

**Response (200 OK)**

```json
{
  "message": "비밀번호가 변경되었습니다."
}
```

**Response (400 Bad Request)**

```json
{
  "current_password": ["현재 비밀번호가 올바르지 않습니다."]
}
```

---

### 3.4 좋아요한 게시글 목록

| 항목           | 내용                    |
| ------------ | --------------------- |
| **Method**   | GET                   |
| **Endpoint** | `/mypage/likes/`      |
| **설명**       | 내가 좋아요한 게시글 목록을 조회합니다 |
| **인증 필요**    | 필요                    |

**Headers**

```
Authorization: Bearer {access_token}
```

**Query Parameters**

- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지당 게시글 수 (기본: 30, 최대: 100)

**Response (200 OK)**

```json
{
  "results": [
    {
      "id": 123,
      "title": "청계천 탐방후기",
      "content": "탁 트인 뷰가 인상적인 곳이에요!",
      "images": ["https://picsum.photos/1080/720?random=1"],
      "author": {
        "id": 2,
        "nickname": "작성자닉네임",
        "profile_image": null
      },
      "place": {
        "cid": "KOP000034",
        "name": "청계천",
        "category": "관광지"
      },
      "like_count": 16,
      "comment_count": 3,
      "view_count": 45,
      "is_liked": true,
      "created_at": "2024-12-25T14:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 2,
    "total_count": 35,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### 3.5 저장한 장소 목록

| 항목           | 내용                           |
| ------------ | ---------------------------- |
| **Method**   | GET                          |
| **Endpoint** | `/mypage/saved-places/`      |
| **설명**       | 내가 저장한 장소 목록을 조회합니다 (최대 10개) |
| **인증 필요**    | 필요                           |

**Headers**

```
Authorization: Bearer {access_token}
```

**Query Parameters**

- `category`: 카테고리 필터 (선택)

**Response (200 OK)**

```json
{
  "results": [
    {
      "cid": "KOP000034",
      "title": "청계천",
      "category_path": "관광 > 명소",
      "address": "서울특별시 중구 청계천로",
      "thumbnail": "https://example.com/place1.jpg"
    }
  ],
  "total": 5,
  "limit": 10
}
```

---

### 3.6 내 게시글 목록

| 항목           | 내용                   |
| ------------ | -------------------- |
| **Method**   | GET                  |
| **Endpoint** | `/mypage/articles/`  |
| **설명**       | 내가 작성한 게시글 목록을 조회합니다 |
| **인증 필요**    | 필요                   |

**Headers**

```
Authorization: Bearer {access_token}
```

**Query Parameters**

- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지당 게시글 수 (기본: 30, 최대: 100)

**Response (200 OK)**

```json
{
  "results": [
    {
      "id": 123,
      "title": "청계천 탐방후기",
      "content": "탁 트인 뷰가 인상적인 곳이에요!",
      "images": ["https://picsum.photos/1080/720?random=1"],
      "place": {
        "cid": "KOP000034",
        "name": "청계천",
        "category": "관광지"
      },
      "like_count": 16,
      "comment_count": 3,
      "view_count": 45,
      "created_at": "2024-12-25T14:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_count": 15,
    "has_next": false,
    "has_previous": false
  }
}
```

---

## 4. 게시글 (Articles)

### 4.1 게시글 목록 조회 (팔로우 피드)

| 항목           | 내용                      |
| ------------ | ----------------------- |
| **Method**   | GET                     |
| **Endpoint** | `/articles/`            |
| **설명**       | 팔로우한 사용자의 게시글 목록을 조회합니다 |
| **인증 필요**    | 필요                      |

**Headers**

```
Authorization: Bearer {access_token}
```

**Query Parameters**

- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지당 게시글 수 (기본: 30, 최대: 100)
- `category`: 카테고리 필터 (예: 카페, 음식점)
- `search`: 검색어 (제목, 내용)

**Response (200 OK)**

```json
{
  "articles": [
    {
      "id": 123,
      "title": "청계천 탐방후기",
      "content": "탁 트인 뷰가 인상적인 곳이에요!",
      "images": ["https://picsum.photos/1080/720?random=1"],
      "hashtags": ["청계천", "데이트", "관광"],
      "author": {
        "id": 2,
        "nickname": "작성자닉네임",
        "profile_image": null
      },
      "place": {
        "cid": "KOP000034",
        "name": "청계천",
        "category": "관광지"
      },
      "like_count": 16,
      "comment_count": 3,
      "view_count": 45,
      "is_liked": false,
      "created_at": "2024-12-25T14:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 142,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### 4.2 게시글 작성

| 항목           | 내용             |
| ------------ | -------------- |
| **Method**   | POST           |
| **Endpoint** | `/articles/`   |
| **설명**       | 새로운 게시글을 작성합니다 |
| **인증 필요**    | 필요             |

**Headers**

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data)**

- `title`: 제목 (필수, 최대 500자)
- `content`: 내용 (필수, 최대 1000자)
- `place_cid`: 장소 ID (필수)
- `hashtags`: 해시태그 배열 (선택, 최대 10개)
- `images`: 이미지 URL 배열 (선택, 최대 5개)

**Request Example**

```json
{
  "title": "청계천 탐방후기",
  "content": "탁 트인 뷰가 인상적인 곳이에요!",
  "place_cid": "KOP000034",
  "hashtags": ["맛집", "청계천", "데이트"],
  "images": ["https://picsum.photos/1080/720?random=1"]
}
```

**Response (201 Created)**

```json
{
  "id": 123,
  "title": "청계천 탐방후기",
  "content": "탁 트인 뷰가 인상적인 곳이에요!",
  "images": ["https://picsum.photos/1080/720?random=1"],
  "hashtags": ["맛집", "청계천", "데이트"],
  "author": {
    "id": 1,
    "nickname": "지구깡유저",
    "profile_image": null
  },
  "place": {
    "cid": "KOP000034",
    "name": "청계천",
    "category": "관광지"
  },
  "like_count": 0,
  "comment_count": 0,
  "view_count": 0,
  "is_liked": false,
  "created_at": "2024-12-26T10:00:00Z"
}
```

**Response (400 Bad Request)**

```json
{
  "title": ["이 필드는 필수 항목입니다."],
  "place_cid": ["유효한 장소 ID를 입력해주세요."]
}
```

---

### 4.3 게시글 상세 조회

| 항목           | 내용                                    |
| ------------ | ------------------------------------- |
| **Method**   | GET                                   |
| **Endpoint** | `/articles/{article_id}/`             |
| **설명**       | 특정 게시글의 상세 정보를 조회합니다. 조회수가 자동으로 증가합니다 |
| **인증 필요**    | 필요                                    |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (200 OK)**

```json
{
  "id": 123,
  "title": "청계천 탐방후기",
  "content": "탁 트인 뷰가 인상적인 곳이에요!",
  "images": ["https://picsum.photos/1080/720?random=1"],
  "hashtags": ["청계천", "데이트", "관광"],
  "author": {
    "id": 2,
    "nickname": "작성자닉네임",
    "profile_image": null
  },
  "place": {
    "cid": "KOP000034",
    "name": "청계천",
    "category": "관광지",
    "address": "서울특별시 중구 청계천로",
    "latitude": 37.5665,
    "longitude": 126.9780
  },
  "like_count": 16,
  "comment_count": 3,
  "view_count": 46,
  "is_liked": false,
  "source": "USER",
  "created_at": "2024-12-25T14:30:00Z",
  "updated_at": "2024-12-25T14:30:00Z"
}
```

**Response (404 Not Found)**

```json
{
  "error": "게시글을 찾을 수 없습니다"
}
```

---

### 4.4 게시글 수정

| 항목           | 내용                            |
| ------------ | ----------------------------- |
| **Method**   | PATCH                         |
| **Endpoint** | `/articles/{article_id}/`     |
| **설명**       | 작성한 게시글을 수정합니다 (장소 정보는 수정 불가) |
| **인증 필요**    | 필요                            |

**Headers**

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data)**

- `title`: 제목 (선택)
- `content`: 내용 (선택)
- `hashtags`: 해시태그 배열 (선택)
- `images`: 추가 이미지 URL 배열 (선택)

**Note**: 장소 정보(`place_cid`)는 수정 불가

**Response (200 OK)**

```json
{
  "id": 123,
  "title": "청계천 탐방후기 (수정)",
  "content": "수정된 내용입니다.",
  "images": ["https://picsum.photos/1080/720?random=1"],
  "hashtags": ["청계천", "데이트"],
  "author": {
    "id": 1,
    "nickname": "지구깡유저",
    "profile_image": null
  },
  "place": {
    "cid": "KOP000034",
    "name": "청계천",
    "category": "관광지"
  },
  "like_count": 16,
  "comment_count": 3,
  "view_count": 46,
  "is_liked": false,
  "created_at": "2024-12-25T14:30:00Z",
  "updated_at": "2024-12-26T11:00:00Z"
}
```

**Response (403 Forbidden)**

```json
{
  "error": "본인이 작성한 게시글만 수정할 수 있습니다"
}
```

---

### 4.5 게시글 삭제

| 항목           | 내용                        |
| ------------ | ------------------------- |
| **Method**   | DELETE                    |
| **Endpoint** | `/articles/{article_id}/` |
| **설명**       | 작성한 게시글을 삭제합니다            |
| **인증 필요**    | 필요                        |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

```
(빈 응답)
```

**Response (403 Forbidden)**

```json
{
  "error": "본인이 작성한 게시글만 삭제할 수 있습니다"
}
```

---

### 4.6 게시글 좋아요 토글

| 항목           | 내용                             |
| ------------ | ------------------------------ |
| **Method**   | POST / DELETE                  |
| **Endpoint** | `/articles/{article_id}/like/` |
| **설명**       | 게시글 좋아요를 추가하거나 취소합니다           |
| **인증 필요**    | 필요                             |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response - POST (201 Created)**

```json
{
  "message": "좋아요 했습니다",
  "is_liked": true,
  "likes_count": 17
}
```

**Response - POST (400 Bad Request)**

```json
{
  "error": "이미 좋아요한 게시글입니다"
}
```

**Response - DELETE (204 No Content)**

```
(빈 응답)
```

**Response - DELETE (400 Bad Request)**

```json
{
  "error": "좋아요하지 않은 게시글입니다"
}
```

---

## 5. 댓글 (Comments)

### 5.1 댓글 목록 조회

| 항목           | 내용                                 |
| ------------ | ---------------------------------- |
| **Method**   | GET                                |
| **Endpoint** | `/articles/{article_id}/comments/` |
| **설명**       | 특정 게시글의 댓글 목록을 조회합니다               |
| **인증 필요**    | 필요                                 |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (200 OK)**

```json
{
  "comments": [
    {
      "id": 1,
      "content": "여기 정말 좋아요!",
      "author_display": "익명1",
      "is_mine": false,
      "created_at": "2024-12-25T15:00:00Z",
      "updated_at": "2024-12-25T15:00:00Z"
    },
    {
      "id": 2,
      "content": "저도 가봤어요",
      "author_display": "익명2",
      "is_mine": true,
      "created_at": "2024-12-25T16:00:00Z",
      "updated_at": "2024-12-25T16:00:00Z"
    }
  ],
  "total": 2
}
```

**Response (404 Not Found)**

```json
{
  "error": "게시글을 찾을 수 없습니다"
}
```

---

### 5.2 댓글 작성

| 항목           | 내용                                 |
| ------------ | ---------------------------------- |
| **Method**   | POST                               |
| **Endpoint** | `/articles/{article_id}/comments/` |
| **설명**       | 게시글에 댓글을 작성합니다 (1게시글 1댓글 원칙)       |
| **인증 필요**    | 필요                                 |

**Headers**

```
Authorization: Bearer {access_token}
```

**Request Body**

```json
{
  "content": "여기 정말 좋아요!"
}
```

**필드 설명**

- `content`: 댓글 내용 (필수, 최대 300자)

**Note**

- 1게시글 1댓글 원칙
- 항상 익명으로 표시

**Response (201 Created)**

```json
{
  "id": 1,
  "content": "여기 정말 좋아요!",
  "author_display": "익명1",
  "is_mine": true,
  "created_at": "2024-12-26T10:00:00Z",
  "updated_at": "2024-12-26T10:00:00Z"
}
```

**Response (400 Bad Request)**

```json
{
  "error": "이미 이 게시글에 댓글을 작성했습니다",
  "existing_comment_id": 2
}
```

---

### 5.3 댓글 수정

| 항목           | 내용                                              |
| ------------ | ----------------------------------------------- |
| **Method**   | PATCH                                           |
| **Endpoint** | `/articles/{article_id}/comments/{comment_id}/` |
| **설명**       | 작성한 댓글을 수정합니다 (본인만 가능)                          |
| **인증 필요**    | 필요                                              |

**Headers**

```
Authorization: Bearer {access_token}
```

**Request Body**

```json
{
  "content": "수정된 댓글 내용"
}
```

**Response (200 OK)**

```json
{
  "id": 1,
  "content": "수정된 댓글 내용",
  "author_display": "익명1",
  "is_mine": true,
  "created_at": "2024-12-26T10:00:00Z",
  "updated_at": "2024-12-26T11:00:00Z"
}
```

**Response (403 Forbidden)**

```json
{
  "error": "본인이 작성한 댓글만 수정할 수 있습니다"
}
```

---

### 5.4 댓글 삭제

| 항목           | 내용                                              |
| ------------ | ----------------------------------------------- |
| **Method**   | DELETE                                          |
| **Endpoint** | `/articles/{article_id}/comments/{comment_id}/` |
| **설명**       | 작성한 댓글을 삭제합니다 (본인만 가능)                          |
| **인증 필요**    | 필요                                              |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

```
(빈 응답)
```

**Response (403 Forbidden)**

```json
{
  "error": "본인이 작성한 댓글만 삭제할 수 있습니다"
}
```

---

## 6. 뽑기 (Draws)

### 6.1 게시글 뽑기 실행

| 항목           | 내용                       |
| ------------ | ------------------------ |
| **Method**   | POST                     |
| **Endpoint** | `/draws/`                |
| **설명**       | 랜덤 또는 AI 기반으로 게시글을 추천합니다 |
| **인증 필요**    | 필요                       |

**Headers**

```
Authorization: Bearer {access_token}
```

**Request Body**

```json
{
  "lat": 37.5665,
  "lng": 126.9780,
  "categories": ["카페", "음식점"],
  "max_distance": 5,
  "mode": "random"
}
```

**필드 설명**

- `lat`: 현재 위치 위도 (필수)
- `lng`: 현재 위치 경도 (필수)
- `categories`: 카테고리 목록 (선택)
- `max_distance`: 최대 거리 km (선택, null이면 제한없음)
- `mode`: 추천 모드 - `random` (완전랜덤) 또는 `ai` (사용자 선호도 기반, 기본: random)

**AI 모드 설명**

- 사용자의 최근 좋아요 기록(최대 20개)을 분석
- 임베딩 벡터를 활용한 코사인 유사도 계산
- 상위 20% 후보군에서 가중 랜덤 선택 (다양성 확보)
- 좋아요 데이터 3개 미만 시 랜덤으로 폴백

**Response (201 Created)**

```json
{
  "article": {
    "id": 123,
    "title": "을지로 숨은 맛집",
    "content": "정말 맛있는 곳입니다",
    "images": ["https://picsum.photos/1080/720?random=1"],
    "hashtags": ["맛집", "을지로"],
    "author": {
      "id": 2,
      "nickname": "작성자닉네임",
      "profile_image": null
    },
    "place": {
      "cid": "KOP000045",
      "name": "OO식당",
      "category": "음식점",
      "address": "서울시 중구 을지로 123",
      "latitude": 37.5665,
      "longitude": 126.9780
    },
    "like_count": 25,
    "comment_count": 5,
    "view_count": 120,
    "is_liked": false,
    "source": "USER",
    "created_at": "2024-12-20T10:00:00Z"
  },
  "distance": 2.3,
  "draw_count": 3
}
```

**Response (400 Bad Request)**

```json
{
  "error": "현재 위치 정보(lat, lng)는 필수입니다"
}
```

**Response (404 Not Found)**

```json
{
  "error": "조건에 맞는 게시글을 찾을 수 없습니다",
  "retry_available": true
}
```

---

### 6.2 뽑기 기록 목록 조회

| 항목           | 내용                  |
| ------------ | ------------------- |
| **Method**   | GET                 |
| **Endpoint** | `/draws/`           |
| **설명**       | 최근 5개의 뽑기 기록을 조회합니다 |
| **인증 필요**    | 필요                  |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (200 OK)**

```json
{
  "history": [
    {
      "draw_id": 1,
      "article": {
        "id": 123,
        "title": "을지로 숨은 맛집",
        "thumbnail": "https://picsum.photos/1080/720?random=1",
        "category": "음식점"
      },
      "place": {
        "cid": "KOP000045",
        "name": "OO식당",
        "address": "서울시 중구 을지로 123"
      },
      "drawn_at": "2024-12-26T10:00:00Z"
    },
    {
      "draw_id": 2,
      "article": {
        "id": 124,
        "title": "홍대 카페",
        "thumbnail": "https://picsum.photos/1080/720?random=2",
        "category": "카페"
      },
      "place": {
        "cid": "KOP000046",
        "name": "XX카페",
        "address": "서울시 마포구 홍대입구"
      },
      "drawn_at": "2024-12-25T15:00:00Z"
    }
  ],
  "total": 2,
  "limit": 5
}
```

**Note**

- `draw_id`는 1부터 시작 (1이 가장 최근)
- 최대 5개까지만 저장됨

---

### 6.3 뽑기 기록 상세 조회

| 항목           | 내용                     |
| ------------ | ---------------------- |
| **Method**   | GET                    |
| **Endpoint** | `/draws/{draw_id}/`    |
| **설명**       | 특정 뽑기 기록의 상세 정보를 조회합니다 |
| **인증 필요**    | 필요                     |

**Headers**

```
Authorization: Bearer {access_token}
```

**Path Parameters**

- `draw_id`: 뽑기 ID (1부터 시작, 1이 가장 최근)

**Response (200 OK)**

```json
{
  "draw_id": 1,
  "article": {
    "id": 123,
    "title": "을지로 숨은 맛집",
    "thumbnail": "https://picsum.photos/1080/720?random=1",
    "category": "음식점"
  },
  "place": {
    "cid": "KOP000045",
    "name": "OO식당",
    "address": "서울시 중구 을지로 123"
  },
  "drawn_at": "2024-12-26T10:00:00Z"
}
```

**Response (404 Not Found)**

```json
{
  "error": "뽑기 기록을 찾을 수 없습니다"
}
```

---

### 6.4 뽑기 기록 삭제

| 항목           | 내용                  |
| ------------ | ------------------- |
| **Method**   | DELETE              |
| **Endpoint** | `/draws/{draw_id}/` |
| **설명**       | 특정 뽑기 기록을 삭제합니다     |
| **인증 필요**    | 필요                  |

**Headers**

```
Authorization: Bearer {access_token}
```

**Path Parameters**

- `draw_id`: 뽑기 ID (1부터 시작, 1이 가장 최근)

**Response (204 No Content)**

```
(빈 응답)
```

**Response (404 Not Found)**

```json
{
  "error": "뽑기 기록을 찾을 수 없습니다"
}
```

---

## 7. 장소 (Places)

### 7.1 장소 목록 조회

| 항목           | 내용                             |
| ------------ | ------------------------------ |
| **Method**   | GET                            |
| **Endpoint** | `/places/`                     |
| **설명**       | 장소 목록을 검색하고 필터링합니다             |
| **인증 필요**    | 선택 (IsAuthenticatedOrReadOnly) |

**Headers**

```
Authorization: Bearer {access_token} (선택)
```

**Query Parameters**

- `search`: 검색어 (제목, 요약)
- `category`: 카테고리 필터 (예: 카페, 음식, 관광)
- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지당 장소 수 (기본: 20, 최대: 50)

**Response (200 OK)**

```json
{
  "results": [
    {
      "cid": "KOP000034",
      "title": "청계천",
      "category_path": "관광 > 명소",
      "address": "서울특별시 중구 청계천로",
      "thumbnail": "https://example.com/place1.jpg"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_count": 200,
    "has_next": true,
    "has_previous": false,
    "page_size": 20
  }
}
```

---

### 7.2 장소 상세 조회

| 항목           | 내용                             |
| ------------ | ------------------------------ |
| **Method**   | GET                            |
| **Endpoint** | `/places/{cid}/`               |
| **설명**       | 특정 장소의 상세 정보를 조회합니다            |
| **인증 필요**    | 선택 (IsAuthenticatedOrReadOnly) |

**Headers**

```
Authorization: Bearer {access_token} (선택)
```

**Response (200 OK)**

```json
{
  "cid": "KOP000034",
  "title": "청계천",
  "category_path": "관광 > 명소",
  "address": "서울특별시 중구 청계천로",
  "address_new": "서울특별시 중구 청계천로",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "phone": "02-1234-5678",
  "opening_hours": "24시간",
  "summary": "서울의 대표적인 도심 하천",
  "images": ["https://example.com/place1.jpg"],
  "is_saved": false
}
```

**Response (404 Not Found)**

```json
{
  "error": "장소를 찾을 수 없습니다"
}
```

---

### 7.3 장소 저장

| 항목           | 내용                          |
| ------------ | --------------------------- |
| **Method**   | POST                        |
| **Endpoint** | `/places/{cid}/save/`       |
| **설명**       | 장소를 내 저장 목록에 추가합니다 (최대 10개) |
| **인증 필요**    | 필요                          |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (201 Created)**

```json
{
  "message": "장소를 저장했습니다",
  "is_saved": true,
  "saved_count": 5
}
```

**Response (400 Bad Request)**

```json
{
  "error": "저장 가능한 최대 개수(10개)를 초과했습니다"
}
```

```json
{
  "error": "이미 저장한 장소입니다"
}
```

**Response (404 Not Found)**

```json
{
  "error": "장소를 찾을 수 없습니다"
}
```

---

### 7.4 장소 저장 취소

| 항목           | 내용                    |
| ------------ | --------------------- |
| **Method**   | DELETE                |
| **Endpoint** | `/places/{cid}/save/` |
| **설명**       | 저장한 장소를 목록에서 제거합니다    |
| **인증 필요**    | 필요                    |

**Headers**

```
Authorization: Bearer {access_token}
```

**Response (200 OK)**

```json
{
  "message": "저장을 취소했습니다",
  "is_saved": false,
  "saved_count": 4
}
```

**Response (404 Not Found)**

```json
{
  "error": "장소를 찾을 수 없습니다"
}
```

---

## 부록

### A. 공통 응답 코드

| 코드  | 의미                    | 설명              |
| --- | --------------------- | --------------- |
| 200 | OK                    | 요청 성공           |
| 201 | Created               | 리소스 생성 성공       |
| 204 | No Content            | 요청 성공, 응답 본문 없음 |
| 400 | Bad Request           | 잘못된 요청          |
| 401 | Unauthorized          | 인증 필요           |
| 403 | Forbidden             | 권한 없음           |
| 404 | Not Found             | 리소스를 찾을 수 없음    |
| 500 | Internal Server Error | 서버 오류           |

---

### B. JWT 토큰 관리

**Access Token**

- 유효기간: 1시간
- 용도: API 요청 인증

**Refresh Token**

- 유효기간: 7일
- 용도: Access Token 갱신

**토큰 갱신 흐름**

1. Access Token 만료 시 401 응답 받음
2. Refresh Token으로 `/auth/token/refresh/` 호출
3. 새로운 Access Token 발급받음
4. 실패 시 재로그인 필요

---

### C. 페이지네이션

모든 목록 조회 API는 페이지네이션을 지원합니다.

**Query Parameters**

- `page`: 페이지 번호 (기본: 1)
- `page_size`: 페이지당 항목 수 (API마다 다름)

**응답 구조**

```json
{
  "results": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 142,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### D. 에러 응답 형식

**단일 필드 에러**

```json
{
  "field_name": ["에러 메시지"]
}
```

**다중 필드 에러**

```json
{
  "username": ["이미 존재하는 사용자명입니다."],
  "password": ["비밀번호가 너무 짧습니다."]
}
```

**일반 에러**

```json
{
  "error": "에러 메시지"
}
```

---

### E. 주요 제약사항

**User 모델**

- 뽑기 기록: 최대 5개
- 저장 장소: 최대 10개

**Article 모델**

- 제목: 최대 500자
- 내용: 최대 1000자
- 해시태그: 최대 10개
- 이미지: 최대 5개

**Comment 모델**

- 내용: 최대 300자
- 1게시글 1댓글 원칙
- 항상 익명 표시

**뽑기 시스템**

- 최근 5개 뽑기 기록과 중복 방지
- AI 모드: 좋아요 3개 이상 필요 (미만 시 랜덤)

---

**문서 버전**: v2.0  
**작성일**: 2025-12-26  
**기반 코드**: 지구깡 프로젝트 깃허브 소스코드
