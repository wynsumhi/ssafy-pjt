<template>
  <div class="article-list-page">
    <div class="container">
      <div class="header-section">
        <h1 class="page-title">탐색하기</h1>
        <p class="page-subtitle">지구깡 멤버들이 공유하는 생생한 장소 후기를 만나보세요.</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else-if="articles.length === 0" class="empty-state">
        <div class="empty-icon">🍃</div>
        <p>팔로우 사용자의 게시글이 없습니다.</p>
        <router-link to="/random" class="btn-write">START RANDOMKKANG!</router-link>
      </div>

      <div v-else class="article-grid">
        <router-link
          v-for="article in articles"
          :key="article.id"
          :to="{ name: 'article-detail', params: { id: article.id } }"
          class="article-card"
        >
          <div class="card-image">
            <img
              :src="
                article.images?.[0] ||
                article.thumbnail ||
                'https://picsum.photos/400/300?random=' + article.id
              "
              :alt="article.title"
              @error="handleImageError"
            />
            <div class="category-badge" v-if="article.place?.category_path">
              {{ article.place.category_path.split('>').pop() }}
            </div>
          </div>

          <div class="card-content">
            <h2 class="article-title">{{ article.title }}</h2>
            <p class="article-excerpt">{{ article.content }}</p>

            <div class="card-footer">
              <div class="user-info">
                <span class="user-avatar">👤</span>
                <span class="username">{{ article.username || '익명' }}</span>
              </div>
              <div class="article-stats">
                <span class="stat-item">❤️ {{ article.like_count || 0 }}</span>
              </div>
            </div>

            <div class="place-info" v-if="article.place">
              <span class="place-name">📍 {{ article.place.title || article.place.title }}</span>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import axiosInstance from '@/api/axios'
import { onMounted, ref } from 'vue'

const articles = ref([])
const loading = ref(true)

const handleImageError = (e) => {
  e.target.src = 'https://picsum.photos/400/300?grayscale'
}

onMounted(async () => {
  try {
    loading.value = true
    const response = await axiosInstance.get('/articles/')

    // 데이터 구조 유연하게 처리
    const data = response.data
    articles.value = data.results || data.articles || (Array.isArray(data) ? data : [])
    console.log('Fetched articles:', articles.value)
  } catch (error) {
    console.error('Error fetching articles:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.article-list-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 60px 20px;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
}

/* 헤더 섹션 */
.header-section {
  margin-bottom: 50px;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 15px;
}

.page-subtitle {
  color: #666;
  font-size: 1.1rem;
}

/* 게시글 그리드 */
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 30px;
}

/* 게시글 카드 디자인 */
.article-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
}

.article-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
}

/* 이미지 영역 */
.card-image {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.article-card:hover .card-image img {
  transform: scale(1.1);
}

.category-badge {
  position: absolute;
  top: 15px;
  left: 15px;
  background: rgba(102, 126, 234, 0.9);
  color: white;
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 0.75rem;
  font-weight: 700;
  backdrop-filter: blur(5px);
}

/* 본문 영역 */
.card-content {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 12px;
  line-height: 1.4;
  /* 2줄 제한 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-excerpt {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 20px;
  /* 3줄 제한 */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 푸터 및 정보 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  background: #eee;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.username {
  font-size: 0.85rem;
  font-weight: 600;
  color: #444;
}

.stat-item {
  font-size: 0.9rem;
  font-weight: 700;
  color: #ff4757;
}

.place-info {
  margin-top: 12px;
}

.place-name {
  font-size: 0.85rem;
  color: #667eea;
  font-weight: 600;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 100px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.btn-write {
  display: inline-block;
  margin-top: 20px;
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 30px;
  font-weight: 700;
}

/* 로딩 스피너 */
.loading-state {
  display: flex;
  justify-content: center;
  padding: 100px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #667eea;
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

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  .article-grid {
    grid-template-columns: 1fr;
  }
}
</style>
