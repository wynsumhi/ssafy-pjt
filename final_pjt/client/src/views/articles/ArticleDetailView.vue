<template>
  <div class="article-detail">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>게시글을 불러오는 중...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="fetchArticle" class="btn-retry">다시 시도</button>
      <router-link to="/" class="btn-home">홈으로 가기</router-link>
    </div>

    <template v-else-if="article">
      <div class="content-wrapper">
        <div class="content-header">
          <div class="category-badge" v-if="article.place?.category_path">
            {{ article.place.category_path }}
          </div>
          <h4 class="title">{{ article.place.summary }}</h4>

          <div class="action-icons">
            <div class="actions">
              <button
                @click="handleLike"
                class="action-btn save"
                :class="{ liked: isLiked }"
                :disabled="likeLoading"
              >
                <span>{{ isLiked ? '❤️' : '🤍' }}</span>
                <span>{{ article.like_count }}</span>
              </button>
            </div>

            <router-link
              v-if="article.place"
              :to="`/places/${article.place.cid}/`"
              class="action-btn place"
              aria-label="장소 상세 보기"
            >
              📍 장소 상세 보기
            </router-link>
          </div>

          <div class="meta-info">
            <div class="author">
              <div class="avatar">👤</div>
              <div class="author-info">
                <span class="author-name">{{ article.author.nickname || '익명' }}</span>
                <span class="date">{{ formatDate(article.created_at) }}</span>
                <span v-if="article.updated_at !== article.created_at" class="edited">
                  (수정됨)
                </span>
              </div>
            </div>
            <div class="actions" v-if="!isAuthor && currentUser">
              <button
                @click="handleFollow"
                class="action-btn follow-btn"
                :class="{ following: isFollowing }"
                :disabled="followLoading"
              >
                <span v-if="isFollowing">✅ Following</span>
                <span v-else>👉 Follow</span>
              </button>
            </div>
          </div>

          <div class="author-actions" v-if="isAuthor">
            <router-link :to="`/articles/${article.id}/edit`" class="btn-edit">
              ✏️ 수정
            </router-link>
            <button @click="handleDelete" class="btn-delete">🗑️ 삭제</button>
          </div>
        </div>

        <h2 class="place-title">{{ article.title }}</h2>

        <div class="image-slider" v-if="displayImages.length > 0">
          <div class="slider-container">
            <img
              :src="displayImages[currentImageIndex]"
              :alt="article.title"
              class="main-image"
              @error="handleImageError"
            />

            <template v-if="displayImages.length > 1">
              <button @click="prevImage" class="slider-btn prev-btn" aria-label="이전 이미지">
                ‹
              </button>
              <button @click="nextImage" class="slider-btn next-btn" aria-label="다음 이미지">
                ›
              </button>

              <div class="slider-indicators">
                <span
                  v-for="(img, index) in displayImages"
                  :key="index"
                  :class="['indicator', { active: index === currentImageIndex }]"
                  @click="currentImageIndex = index"
                  :aria-label="`이미지 ${index + 1}`"
                ></span>
              </div>
            </template>
          </div>
        </div>

        <div class="content-body">
          <p>{{ article.content }}</p>
        </div>

        <div class="hashtags" v-if="parsedTags.length > 0">
          <span v-for="tag in parsedTags" :key="tag" class="hashtag"> #{{ tag }} </span>
        </div>

        <div class="comments-section">
          <h3>댓글 {{ commentTotal }}개</h3>

          <div class="comment-form-container">
            <div v-if="!currentUser" class="comment-notice">
              댓글을 작성하려면 <router-link to="/login">로그인</router-link>이 필요합니다.
            </div>
            <div v-else-if="hasAlreadyCommented" class="comment-notice already">
              이미 이 게시글에 댓글을 작성하셨습니다. (1인 1댓글 제한)
            </div>
            <div v-else class="comment-form">
              <textarea
                v-model="newCommentContent"
                placeholder="따뜻한 댓글을 남겨주세요."
              ></textarea>
              <div class="form-actions">
                <button
                  @click="submitComment"
                  :disabled="!newCommentContent.trim()"
                  class="btn-submit"
                >
                  등록
                </button>
              </div>
            </div>
          </div>

          <div v-if="comments && comments.length > 0" class="comments-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-meta">
                <span class="comment-author">{{ comment.author_display || '익명' }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>

              <div v-if="editingCommentId === comment.id" class="edit-mode">
                <textarea v-model="editContent"></textarea>
                <div class="edit-actions">
                  <button @click="updateComment(comment.id)" class="btn-save">저장</button>
                  <button @click="cancelEdit" class="btn-cancel">취소</button>
                </div>
              </div>
              <div v-else class="comment-content">
                {{ comment.content }}
              </div>

              <div v-if="comment.is_mine" class="comment-utils">
                <button @click="startEdit(comment)">수정</button>
                <button @click="deleteComment(comment.id)" class="btn-del">삭제</button>
              </div>
            </div>
          </div>
          <div v-else class="no-comments">아직 댓글이 없습니다. 첫 번째 댓글을 남겨보세요!</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { getArticleDetail } from '@/api/articles'
import { authAPI } from '@/api/auth'
import axiosInstance from '@/api/axios'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 기본 상태
const article = ref(null)
const currentUser = ref(null)
const loading = ref(true)
const error = ref(null)

// 좋아요/팔로우 상태
const likeLoading = ref(false)
const followLoading = ref(false)
const isLiked = ref(false)
const isFollowing = ref(false)

// 이미지 슬라이더
const currentImageIndex = ref(0)
const imagesArray = ref([])

// 댓글 상태
const comments = ref([])
const commentTotal = ref(0)
const newCommentContent = ref('')
const editingCommentId = ref(null)
const editContent = ref('')

// 1. 좋아요 기능 구현
const handleLike = async () => {
  if (!currentUser.value) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }
  if (likeLoading.value) return

  likeLoading.value = true
  const articleId = article.value.id

  try {
    if (isLiked.value) {
      // 좋아요 취소 (DELETE)
      const response = await axiosInstance.delete(`/articles/${articleId}/like/`)
      isLiked.value = false
      // 백엔드 응답 명세에 likes_count가 있을 경우 연동
      article.value.like_count = response.data.likes_count ?? article.value.like_count - 1
    } else {
      // 좋아요 (POST)
      const response = await axiosInstance.post(`/articles/${articleId}/like/`)
      isLiked.value = true
      article.value.like_count = response.data.likes_count ?? article.value.like_count + 1
    }
  } catch (err) {
    console.error('좋아요 처리 오류:', err)
    alert('좋아요 처리에 실패했습니다.')
  } finally {
    likeLoading.value = false
  }
}

// 팔로우 기능 구현
const handleFollow = async () => {
  if (!currentUser.value) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }
  if (followLoading.value) return

  followLoading.value = true
  const userId = article.value.author?.id ?? article.value.user // 게시글 작성자의 ID

  try {
    if (isFollowing.value) {
      // 언팔로우 (DELETE)
      await axiosInstance.delete(`/users/${userId}/follow/`)
    } else {
      // 팔로우 (POST)
      await axiosInstance.post(`/users/${userId}/follow/`)
    }

    // 성공 시 최신 게시글 상태로 갱신하여 is_following 동기화
    await fetchArticle()
  } catch (err) {
    console.error('팔로우 처리 오류:', err)
    const msg = err.response?.data?.error || '팔로우 처리에 실패했습니다.'
    alert(msg)
  } finally {
    followLoading.value = false
  }
}

// 작성자 확인
const isAuthor = computed(() => {
  if (!currentUser.value || !article.value) return false
  const authorId = article.value.author?.id ?? article.value.user
  return currentUser.value.id === authorId
})

// 태그 파싱
const parsedTags = computed(() => {
  if (!article.value?.tags) return []
  return Array.isArray(article.value.tags) ? article.value.tags : []
})

// 이미지 계산
const displayImages = computed(() => {
  const imgs = []
  if (article.value?.images?.length > 0) {
    imgs.push(...article.value.images)
  }
  if (imgs.length === 0 && article.value?.place?.related_images) {
    imgs.push(...article.value.place.related_images)
  }
  return imgs.length > 0 ? imgs : ['https://picsum.photos/1200/600/']
})

const hasAlreadyCommented = computed(() => {
  if (!comments.value) return false
  return comments.value.some((c) => c.is_mine === true)
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 댓글 데이터 가져오기
const fetchComments = async () => {
  const articleId = route.params.id
  try {
    const response = await axiosInstance.get(`/articles/${articleId}/comments/`)
    comments.value = response.data?.comments || []
    commentTotal.value = response.data?.total || 0
  } catch (err) {
    console.error('댓글 로딩 오류:', err)
    comments.value = []
  }
}

// 게시글 상세 데이터 가져오기
const fetchArticle = async () => {
  const articleId = route.params.id
  loading.value = true
  error.value = null

  try {
    const response = await getArticleDetail(articleId)
    // 데이터 로드 성공
    const data = response.data
    article.value = data

    // 초기 상태 설정 (데이터가 없을 경우를 대비해 기본값 설정)
    isLiked.value = data.is_liked || false
    isFollowing.value = data.is_following || false

    // 이미지 배열 설정
    imagesArray.value = data.images || []

    // 댓글 로드
    await fetchComments()
  } catch (err) {
    console.error('게시글 로딩 상세 정보:', err.response)
    // 에러 발생 시 사용자에게 보여줄 메시지
    error.value = err.response?.data?.message || '게시글을 불러오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

const fetchCurrentUser = async () => {
  try {
    currentUser.value = await authAPI.getUserInfo()
  } catch (err) {
    console.log('비로그인 사용자')
    console.error(err)
  }
}

// 댓글 로직들
const submitComment = async () => {
  if (!newCommentContent.value.trim()) return
  const articleId = route.params.id
  try {
    await axiosInstance.post(`/articles/${articleId}/comments/`, {
      content: newCommentContent.value,
    })
    newCommentContent.value = ''
    await fetchComments()
  } catch (err) {
    console.error(err)
    alert('댓글 작성에 실패했습니다.')
  }
}

const startEdit = (comment) => {
  editingCommentId.value = comment.id
  editContent.value = comment.content
}

const cancelEdit = () => {
  editingCommentId.value = null
  editContent.value = ''
}

const updateComment = async (commentId) => {
  const articleId = route.params.id
  try {
    await axiosInstance.patch(`/articles/${articleId}/comments/${commentId}/`, {
      content: editContent.value,
    })
    editingCommentId.value = null
    await fetchComments()
  } catch (err) {
    console.error(err)
    alert('댓글 수정에 실패했습니다.')
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return
  const articleId = route.params.id
  try {
    await axiosInstance.delete(`/articles/${articleId}/comments/${commentId}/`)
    await fetchComments()
  } catch (err) {
    console.error(err)
    alert('댓글 삭제에 실패했습니다.')
  }
}

const handleDelete = async () => {
  if (!confirm('게시글을 삭제하시겠습니까?')) return
  try {
    await axiosInstance.delete(`/articles/${article.value.id}/`)
    router.push('/')
  } catch (err) {
    console.error(err)
    alert('게시글 삭제 실패')
  }
}

const nextImage = () => {
  currentImageIndex.value = (currentImageIndex.value + 1) % displayImages.value.length
}
const prevImage = () => {
  currentImageIndex.value =
    currentImageIndex.value === 0 ? displayImages.value.length - 1 : currentImageIndex.value - 1
}

const handleImageError = (e) => {
  e.target.src = 'https://picsum.photos/1200/600/'
}

onMounted(async () => {
  await fetchCurrentUser()
  await fetchArticle()
})
</script>

<style scoped>
.article-detail {
  min-height: 100vh;
  background: #fff;
}
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 20px;
}
.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 20px;
  padding: 40px;
  text-align: center;
}
.btn-retry {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  text-decoration: none;
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
  background: #ffffff;
  padding: 50px;
}
.content-header {
  margin-bottom: 40px;
}
.category-badge {
  font-size: 16px;
  font-weight: 700;
  color: #2563eb;
  text-align: center;
}
.title {
  font-size: 32px;
  margin: 8px;
  color: #333;
  line-height: 1.6;
  text-align: center;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
}
.author {
  display: flex;
  align-items: center;
  gap: 15px;
}
.avatar {
  width: 50px;
  height: 50px;
  background: #f0f0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}
.author-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.author-name {
  font-weight: 700;
  color: #1a1a1a;
}
.date {
  color: #999;
  font-size: 0.9rem;
}

/* 팔로우 버튼 스타일 */
.follow-btn {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  border: none;
  background: #f0faf6;
  color: #027648;
  transition: all 0.3s;
}
.action-btn.follow-btn {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  border: none;
  background: #fff9e7;
  color: #dd7d02;
  transition: all 0.3s;
}
.follow-btn.following {
  background: #f0faf6;
  color: #027648;
}
.follow-btn:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

.action-icons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 24px 0 48px;
}
.action-btn {
  padding: 10px 20px;
  background: #e3f2fd;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  transition: all 0.2s;
  color: #1976d2;
  height: 100%;
}
.action-btn.liked {
  background: #ffe3e3;
  color: #ff4757;
}
.action-btn.place {
  background: #e3f2fd;
  color: #1976d2;
  text-decoration: none;
}

.author-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}
.btn-edit {
  background: #3498db;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9rem;
}
.btn-delete {
  background: white;
  color: #e74c3c;
  border: 2px solid #e74c3c;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.image-slider {
  position: relative;
  width: 100%;
  background: #000;
  margin: 14px 0 40px;
}
.slider-container {
  position: relative;
  width: 100%;
  height: 500px;
  overflow: hidden;
}
.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.slider-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 10;
}
.prev-btn {
  left: 20px;
}
.next-btn {
  right: 20px;
}
.slider-indicators {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}
.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
}
.indicator.active {
  background: white;
  width: 24px;
  border-radius: 4px;
}

.content-body {
  line-height: 2;
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 50px;
  white-space: pre-line;
}
.hashtags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 20px 0;
  border-top: 1px solid #e0e0e0;
}
.hashtag {
  padding: 6px 14px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  font-size: 0.85rem;
}

.comment-form-container {
  margin: 20px 0;
}

.comments-section {
  margin-top: 60px;
  border-top: 2px solid #eee;
  padding-top: 40px;
}
.comment-form textarea {
  width: 100%;
  min-height: 100px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 10px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
}
.btn-submit {
  padding: 10px 25px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-submit:hover {
  background: #5568d3;
}
.comment-item {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}
.comment-author {
  font-weight: 700;
  margin-right: 10px;
}
.comment-date {
  color: #999;
  font-size: 0.8rem;
}
.comment-utils {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}
.comment-utils button {
  background: none;
  border: none;
  color: #888;
  font-size: 0.8rem;
  cursor: pointer;
}
/* 댓글 안내 문구 스타일 */
.comment-notice {
  padding: 20px;
  background: transparent;
  border-radius: 8px;
  text-align: center;
  color: #666;
  margin-bottom: 20px;
  font-weight: 500;
}

/* 이미 작성했을 때의 강조 스타일 (Red 컬러) */
.comment-notice.already {
  background: #fff5f5;
  color: #e74c3c;
  border: 1px solid #ffc9c9;
  margin: 10px 0;
}

/* 로그인 링크 스타일 */
.comment-notice a {
  color: #667eea;
  text-decoration: underline;
  font-weight: 700;
}
</style>
