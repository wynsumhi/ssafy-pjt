<template>
  <div class="my-articles">
    <div class="container">
      <div class="header-section">
        <button @click="$router.back()" class="btn-back">← 뒤로가기</button>
        <h1 class="page-title">내 게시글 목록</h1>
        <p class="page-subtitle">총 {{ pagination.total_count }}개의 이야기를 공유하셨습니다.</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>게시글을 불러오는 중입니다...</p>
      </div>

      <div v-else-if="articles.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>아직 작성한 게시글이 없습니다.</p>
        <router-link to="/articles/create" class="btn-create">첫 글 쓰러 가기</router-link>
      </div>

      <div v-else class="content-section">
        <div class="article-grid">
          <div
            v-for="article in articles"
            :key="article.id"
            class="article-card"
            @click="goToDetail(article.id)"
          >
            <div class="article-image">
              <img
                :src="article.images?.[0] || 'https://picsum.photos/400/300'"
                alt="article thumbnail"
              />
              <div class="article-category" v-if="article.place?.category_path">
                {{ article.place.category_path.split('>').pop() }}
              </div>
            </div>

            <div class="article-info">
              <h3 class="article-title">{{ article.title }}</h3>
              <p class="article-excerpt">{{ article.content }}</p>

              <div class="article-meta">
                <span class="date">{{ formatDate(article.created_at) }}</span>
                <div class="stats">
                  <span>❤️ {{ article.like_count || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="pagination" v-if="pagination.total_pages > 1">
          <button
            :disabled="!pagination.has_previous"
            @click="changePage(pagination.current_page - 1)"
            class="page-btn"
          >
            이전
          </button>

          <span class="page-info"
            >{{ pagination.current_page }} / {{ pagination.total_pages }}</span
          >

          <button
            :disabled="!pagination.has_next"
            @click="changePage(pagination.current_page + 1)"
            class="page-btn"
          >
            다음
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// API 베이스 URL 설정
axios.defaults.baseURL = 'http://localhost:8000/api/v1'

const articles = ref([])
const loading = ref(true)
const pagination = ref({
  current_page: 1,
  total_pages: 0,
  total_count: 0,
  has_next: false,
  has_previous: false,
})

// 게시글 데이터 가져오기
const fetchMyArticles = async (page = 1) => {
  loading.value = true
  // 로컬 스토리지 등에서 토큰 가져오기
  const token = localStorage.getItem('access_token')

  try {
    const response = await axios.get(`/mypage/articles/?page=${page}`, {
      headers: {
        // 백엔드 설정에 따라 'Bearer ' 또는 'Token ' 등을 붙여야 합니다.
        Authorization: `Bearer ${token}`,
      },
    })
    articles.value = response.data.results
    pagination.value = response.data.pagination
  } catch (error) {
    if (error.response?.status === 401) {
      alert('로그인이 만료되었습니다. 다시 로그인해주세요.')
      router.push('/login')
    }
    console.error('내 게시글 로딩 실패:', error)
  } finally {
    loading.value = false
  }
}

// 상세 페이지 이동
const goToDetail = (id) => {
  router.push(`/articles/${id}`)
}

// 페이지 변경
const changePage = (newPage) => {
  fetchMyArticles(newPage)
  window.scrollTo(0, 0)
}

// 날짜 포맷
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
  fetchMyArticles()
})
</script>

<style scoped>
.my-articles {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 40px 20px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

/* 헤더 */
.header-section {
  margin-bottom: 40px;
}

.btn-back {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 15px;
  padding: 0;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #666;
}

/* 게시글 그리드 */
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.article-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
  cursor: pointer;
}

.article-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.article-image {
  position: relative;
  height: 200px;
}

.article-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.article-category {
  position: absolute;
  top: 15px;
  left: 15px;
  background: rgba(102, 126, 234, 0.9);
  color: white;
  padding: 5px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.article-info {
  padding: 20px;
}

.article-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-excerpt {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.date {
  font-size: 0.85rem;
  color: #999;
}

.stats {
  font-weight: 600;
  color: #ff4757;
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
}

.page-btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-weight: 600;
  color: #333;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.btn-create {
  display: inline-block;
  margin-top: 20px;
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 700;
}

/* 로딩 스피너 */
.loading-state {
  text-align: center;
  padding: 50px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  margin: 0 auto 20px;
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

@media (max-width: 768px) {
  .article-grid {
    grid-template-columns: 1fr;
  }
}
</style>
