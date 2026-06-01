<template>
  <div class="liked-articles">
    <div class="container">
      <div class="header-section">
        <button @click="$router.back()" class="btn-back">← 뒤로가기</button>
        <h1 class="page-title">❤️ 좋아요 한 글</h1>
        <p class="page-subtitle">
          내가 공감 버튼을 누른 {{ pagination.total_count }}개의 게시글입니다.
        </p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>목록을 불러오는 중입니다...</p>
      </div>

      <div v-else-if="articles.length === 0" class="empty-state">
        <div class="empty-icon">🤍</div>
        <p>아직 좋아요를 표시한 게시글이 없습니다.</p>
        <router-link to="/" class="btn-home">새로운 글 탐색하기</router-link>
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
              <img :src="article.thumbnail || 'https://picsum.photos/400/300'" alt="thumbnail" />
              <div class="author-badge">{{ article.place.category_path }}</div>
            </div>

            <div class="article-info">
              <h3 class="article-title">{{ article.title }}</h3>
              <p class="article-excerpt">{{ article.summary }}</p>

              <div class="article-meta">
                <span class="place-name">📍 {{ article.place?.title || '장소 정보 없음' }}</span>
                <div class="stats">
                  <span class="heart">❤️ {{ article.like_count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="pagination" v-if="pagination.total_pages > 1">
          <button
            :disabled="!pagination.has_previous"
            @click="fetchLikedArticles(pagination.current_page - 1)"
            class="page-btn"
          >
            이전
          </button>

          <span class="page-info"
            >{{ pagination.current_page }} / {{ pagination.total_pages }}</span
          >

          <button
            :disabled="!pagination.has_next"
            @click="fetchLikedArticles(pagination.current_page + 1)"
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

// 상태 관리
const articles = ref([])
const loading = ref(true)
const pagination = ref({
  current_page: 1,
  total_pages: 0,
  total_count: 0,
  has_next: false,
  has_previous: false,
})

// 좋아요 목록 가져오기
const fetchLikedArticles = async (page = 1) => {
  loading.value = true
  const token = localStorage.getItem('access_token')

  try {
    const response = await axios.get(`/mypage/likes/?page=${page}`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    // API 명세의 { results, pagination } 구조 반영
    articles.value = response.data.results
    pagination.value = response.data.pagination
  } catch (error) {
    if (error.response?.status === 401) {
      alert('로그인이 만료되었습니다.')
      router.push('/login')
    } else {
      console.error('좋아요 목록 로드 실패:', error)
    }
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/articles/${id}`)
}

onMounted(() => {
  fetchLikedArticles()
})
</script>

<style scoped>
.liked-articles {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 40px 20px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

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
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 8px;
}
.page-subtitle {
  color: #666;
}

/* 카드 그리드 */
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.article-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.article-card:hover {
  transform: translateY(-8px);
}

.article-image {
  position: relative;
  height: 180px;
}
.article-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-badge {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
}

.article-info {
  padding: 20px;
}
.article-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 10px;
}
.article-excerpt {
  color: #777;
  font-size: 0.9rem;
  line-height: 1.4;
  height: 2.8em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 15px;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.place-name {
  font-size: 0.85rem;
  color: #667eea;
  font-weight: 600;
}
.heart {
  color: #ff4757;
  font-weight: 700;
}

/* 페이지네이션 & 상태 스타일 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
}
.page-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 100px 20px;
  background: white;
  border-radius: 20px;
}
.empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}
.btn-home {
  display: inline-block;
  margin-top: 15px;
  color: #667eea;
  font-weight: 700;
}

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
  margin: 0 auto 15px;
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
</style>
