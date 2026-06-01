<template>
  <div class="saved-places">
    <div class="container">
      <div class="header-section">
        <button @click="$router.back()" class="btn-back">← 뒤로가기</button>
        <h1 class="page-title">저장한 장소</h1>
        <p class="page-subtitle">다시 방문하고 싶은 {{ totalCount }}개의 장소를 모아봤어요.</p>
      </div>

      <div class="filter-section">
        <button
          v-for="cat in categories"
          :key="cat.value"
          :class="['filter-btn', { active: selectedCategory === cat.value }]"
          @click="handleCategoryChange(cat.value)"
        >
          {{ cat.label }}
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>장소를 불러오는 중입니다...</p>
      </div>

      <div v-else-if="places.length === 0" class="empty-state">
        <div class="empty-icon">📍</div>
        <p v-if="selectedCategory === ''">아직 저장한 장소가 없습니다.</p>
        <p v-else>'{{ getCategoryLabel(selectedCategory) }}' 카테고리에 저장된 장소가 없습니다.</p>
        <router-link to="/random" class="btn-write">START RANDOMKKANG!</router-link>
      </div>

      <div v-else class="content-section">
        <div class="place-grid">
          <div
            v-for="place in places"
            :key="place.id"
            class="place-card"
            @click="goToPlaceDetail(place.cid)"
          >
            <div class="place-image">
              <img :src="getPlaceThumbnail(place)" :alt="place.title || 'place thumbnail'" />
              <div class="place-badge">{{ place.category_path || '장소' }}</div>
            </div>

            <div class="place-info">
              <h3 class="place-name">{{ place.title }}</h3>
              <p class="place-address">{{ place.address_new }}</p>
              <div class="place-footer">
                <span class="phone" v-if="place.phone">{{ place.phone }}</span>
                <span class="save-tag">⭐ 저장됨</span>
              </div>
            </div>
          </div>
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
const places = ref([])
const totalCount = ref(0)
const loading = ref(true)
const selectedCategory = ref('') // 현재 선택된 필터

// 카테고리 옵션 (백엔드 데이터 구조에 맞춰 수정 가능)
const categories = [
  { label: '전체', value: '' },
  { label: '음식점', value: '음식' },
  { label: '카페', value: '카페' },
  { label: '쇼핑', value: '쇼핑' },
  { label: '문화관광', value: '문화관광' },
  { label: '숙박', value: '숙박' },
  { label: '자연명소', value: '자연명소' },
  { label: '축제 행사 공연', value: '축제' },
  { label: '역사 유적지', value: '역사' },
]

// 카테고리 라벨 찾기
const getCategoryLabel = (val) => categories.find((c) => c.value === val)?.label

// 썸네일 추출 (main_image URL 우선, 없으면 랜덤 플레이스홀더)
const getPlaceThumbnail = (place) => {
  try {
    if (
      place?.main_image &&
      typeof place.main_image === 'string' &&
      place.main_image.trim() !== ''
    ) {
      return place.main_image
    }
    return `https://picsum.photos/400/300?random=${place?.id ?? Math.floor(Math.random() * 10000)}`
  } catch (err) {
    console.error('썸네일 로딩 오류:', err)
    return `https://picsum.photos/400/300?random=${place?.id ?? Math.floor(Math.random() * 10000)}`
  }
}

// 데이터 가져오기 함수
const fetchSavedPlaces = async (category = '') => {
  loading.value = true
  const token = localStorage.getItem('access_token') // 토큰 가져오기

  try {
    const response = await axios.get('/mypage/saved-places/', {
      params: { category: category }, // 쿼리 파라미터 전달
      headers: {
        Authorization: `Bearer ${token}`, // 인증 헤더 추가
      },
    })

    // API 명세의 { results, total } 구조 반영
    places.value = response.data.results || []
    totalCount.value = response.data.total || 0
  } catch (error) {
    if (error.response?.status === 401) {
      alert('로그인이 필요한 서비스입니다.')
      router.push('/login')
    } else {
      console.error('장소 로딩 실패:', error)
    }
  } finally {
    loading.value = false
  }
}

// 필터 변경 핸들러
const handleCategoryChange = (categoryValue) => {
  selectedCategory.value = categoryValue
  fetchSavedPlaces(categoryValue)
}

// 장소 상세 이동 (카카오 CID 등을 활용)
const goToPlaceDetail = (cid) => {
  router.push(`/places/${cid}`)
}

onMounted(() => {
  fetchSavedPlaces()
})
</script>

<style scoped>
.saved-places {
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
  margin-bottom: 30px;
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

/* 필터 섹션 */
.filter-section {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  overflow-x: auto;
  padding-bottom: 10px;
  -ms-overflow-style: none; /* IE/Edge */
  scrollbar-width: none; /* Firefox */
}

.filter-section::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.filter-btn {
  padding: 10px 20px;
  border-radius: 25px;
  border: 1px solid #ddd;
  background: white;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  color: #666;
}

.filter-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
}

/* 장소 그리드 */
.place-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.place-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
  cursor: pointer;
}

.place-card:hover {
  transform: translateY(-8px);
}

.place-image {
  position: relative;
  height: 180px;
}

.place-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.place-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #333;
}

.place-info {
  padding: 20px;
}

.place-name {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1a1a1a;
}

.place-address {
  font-size: 0.9rem;
  color: #777;
  margin-bottom: 15px;
  line-height: 1.4;
}

.place-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.phone {
  font-size: 0.8rem;
  color: #999;
}

.save-tag {
  font-size: 0.85rem;
  color: #f1c40f;
  font-weight: 700;
}

/* 빈 상태 및 로딩 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 25px;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.btn-home {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 25px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 10px;
}

.loading-state {
  text-align: center;
  padding: 40px;
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

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 600px) {
  .place-grid {
    grid-template-columns: 1fr;
  }
}
</style>
