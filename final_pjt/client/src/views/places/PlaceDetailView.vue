<template>
  <div class="place-detail">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>장소 정보를 불러오는 중...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <div class="error-icon">📍</div>
      <p>{{ error }}</p>
      <button @click="fetchPlaceDetail" class="btn-retry">다시 시도</button>
      <router-link to="/" class="btn-home">홈으로 가기</router-link>
    </div>

    <template v-else-if="place">
      <div class="content-wrapper">
        <div class="content-header">
          <div class="category-badge" v-if="place.category_path">
            {{ place.category_path }}
          </div>
          <h1 class="title">{{ place.title }}</h1>

          <div class="meta-info">
            <div class="rating-info" v-if="place.raw_data?.local_business?.aggregateRating">
              <span class="star">⭐</span>
              <span class="score">{{
                place.raw_data.local_business.aggregateRating.ratingValue
              }}</span>
              <span class="count"
                >({{ place.raw_data.local_business.aggregateRating.ratingCount }})</span
              >
            </div>
            <div class="actions">
              <button @click="toggleSave" class="action-btn btn-save" :class="{ active: isSaved }">
                <span>{{ isSaved ? '⭐' : '☆' }}</span>
                <span>저장</span>
              </button>
              <button @click="sharePlace" class="action-btn btn-share">
                <span>🔗</span>
                <span>공유</span>
              </button>
            </div>
          </div>
        </div>

        <div class="image-slider" v-if="displayImages.length > 0">
          <div class="slider-container">
            <img
              :src="displayImages[currentImageIndex]"
              :alt="place.title"
              class="main-image"
              @error="handleImageError"
            />

            <template v-if="displayImages.length > 1">
              <button @click="prevImage" class="slider-btn prev-btn">‹</button>
              <button @click="nextImage" class="slider-btn next-btn">›</button>

              <div class="slider-indicators">
                <span
                  v-for="(img, index) in displayImages"
                  :key="index"
                  :class="['indicator', { active: index === currentImageIndex }]"
                  @click="currentImageIndex = index"
                ></span>
              </div>
            </template>
          </div>
        </div>

        <div class="summary-box" v-if="place.summary">
          <div class="summary-content">
            <h4 class="summary-text">{{ place.summary }}</h4>
          </div>
        </div>

        <div class="info-grid">
          <div class="info-row">
            <span class="info-label">주소</span>
            <span class="info-value">
              {{ place.address_new }}
              <div class="old-address">({{ place.address }})</div>
            </span>
          </div>
          <div class="info-row" v-if="place.phone">
            <span class="info-label">전화번호</span>
            <span class="info-value">{{ place.phone }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">이용시간</span>
            <span class="info-value">{{
              place.opening_hours || '상시 개방 (우천 시 통제 가능)'
            }}</span>
          </div>
          <div class="info-row" v-if="place.fee_info">
            <span class="info-label">입장료</span>
            <span class="info-value">{{ place.fee_info }}</span>
          </div>
        </div>

        <div class="content-body">
          <h3 class="section-title">장소 소개</h3>
          <div class="description-text" v-html="place.raw_data.post_desc"></div>
        </div>

        <div class="hashtags" v-if="place.tags && place.tags.length > 0">
          <span v-for="tag in place.tags" :key="tag" class="hashtag"> #{{ tag.trim() }} </span>
        </div>

        <div class="location-section">
          <h3 class="section-title">찾아오는 길</h3>
          <div class="subway-info">🚇 {{ place.subway_info }}</div>
          <!-- 지도 임베딩 예정 -->
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import axiosInstance from '@/api/axios'
import { getPlaceDetail } from '@/api/places'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const place = ref(null)
const loading = ref(true)
const error = ref(null)
const currentImageIndex = ref(0)
const isSaved = ref(false)

const displayImages = computed(() => {
  const imgs = []
  if (place.value?.main_image) imgs.push(place.value.main_image)
  if (place.value?.related_images?.length > 0) imgs.push(...place.value.related_images)
  return imgs.length > 0 ? imgs : ['https://picsum.photos/1200/600/']
})

const fetchPlaceDetail = async () => {
  // route.params에서 place_cid 또는 id를 가져옵니다.
  const placeCid = route.params.place_cid || route.params.id
  if (!placeCid) return

  loading.value = true
  error.value = null

  try {
    const response = await getPlaceDetail(placeCid)
    place.value = response.data
    isSaved.value = response.data?.is_saved || false
  } catch (err) {
    console.error('데이터 로딩 오류:', err)
    error.value = '장소 정보를 불러오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// 새로고침이나 URL 변경 대응을 위한 watch
watch(
  () => route.params.place_cid,
  () => {
    fetchPlaceDetail()
  },
)

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

const toggleSave = () => {
  if (!place.value?.cid) {
    alert('장소 정보를 불러올 수 없습니다.')
    return
  }

  if (isSaved.value) {
    // 이미 저장된 경우 DELETE 요청
    axiosInstance
      .delete(`/places/${place.value.cid}/save/`)
      .then(() => {
        isSaved.value = false
      })
      .catch((err) => {
        console.error('장소 저장 취소 오류:', err)
        alert('장소 저장 취소에 실패했습니다. 다시 시도해주세요.')
      })
  } else {
    // 저장되지 않은 경우 POST 요청
    axiosInstance
      .post(`/places/${place.value.cid}/save/`)
      .then(() => {
        isSaved.value = true
      })
      .catch((err) => {
        console.error('장소 저장 오류:', err)
        alert('장소 저장에 실패했습니다. 다시 시도해주세요.')
      })
  }
}

onMounted(() => {
  fetchPlaceDetail()
})
</script>

<style scoped>
.place-detail {
  min-height: 100vh;
  background: #fff;
}

/* 콘텐츠 래퍼 */
.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  padding: 50px;
}

/* 헤더 */
.content-header {
  margin-bottom: 30px;
}

.category-badge {
  font-size: 16px;
  font-weight: 700;
  color: #2563eb;
  text-align: center;
}

.title {
  font-size: 48px;
  margin: 8px;
  color: #333;
  line-height: 1.6;
  text-align: center;
  word-break: keep-all;
  text-wrap: balance;
}

.meta-info {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}
.rating-info {
  display: flex;
  align-items: center;
  gap: 6px;
}
.star {
  color: #fbbf24;
  font-size: 1.2rem;
}
.score {
  font-weight: 800;
  font-size: 1.2rem;
}
.count {
  color: #999;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 25px 0;
}

.action-btn {
  padding: 10px 20px;
  background: #e6e7f3;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  transition: all 0.3s;
}

.action-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

/* 저장 버튼 (하트 스타일) */
.btn-save {
  background: #ffe3e3;
  color: #ff4757;
  padding: 8px 14px;
  border-radius: 18px;
  font-weight: 800;
}
.btn-save:hover { background: #ffd6d6; }
.btn-save.active { background: #ffdddd; box-shadow: 0 6px 12px rgba(255,71,87,0.08); }

/* 공유 버튼 (라이트 블루) */
.btn-share {
  background: #e3f2fd;
  color: #1976d2;
  padding: 8px 14px;
  border-radius: 18px;
  font-weight: 700;
}
.btn-share:hover { background: #d0eefd; }

/* 이미지 슬라이더 */
.image-slider {
  margin: 10px 0 20px;
  position: relative;
  background: #000;
}
.slider-container {
  height: 500px;
  position: relative;
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
  width: 44px;
  height: 44px;
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

/* 요약 박스 */
.summary-box {
  display: flex;
  background: #f9fafb;
  margin-bottom: 30px;
}
.summary-icon {
  font-size: 1.5rem;
}
.summary-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

/* 상세 정보 그리드 */
.info-grid {
  margin-bottom: 40px;
  border-top: 1px solid #eee;
}
.info-row {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}
.info-label {
  width: 120px;
  font-weight: 700;
  color: #6b7280;
}
.info-value {
  flex: 1;
  color: #111827;
  line-height: 1.5;
}
.old-address {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-top: 4px;
}

/* 본문 */
.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 20px;
}
.description-text {
  line-height: 1.8;
  font-size: 1.1rem;
  color: #374151;
}

/* 해시태그 */
.hashtags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 30px 0;
}
.hashtag {
  padding: 6px 14px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  font-size: 0.85rem;
}

/* 위치 정보 */
.location-box {
  background: #f9fafb;
  padding: 20px;
  border-radius: 12px;
}
.subway-info {
  font-weight: 700;
  color: #6366f1;
  margin-bottom: 15px;
}
.location-actions {
  display: flex;
  gap: 10px;
}
.map-button {
  flex: 1;
  padding: 12px;
  text-align: center;
  border-radius: 8px;
  border: 1px solid #6366f1;
  color: #6366f1;
  text-decoration: none;
  font-weight: 700;
  transition: 0.2s;
}
.map-button:hover {
  background: #6366f1;
  color: white;
}
.map-button.google {
  border-color: #4285f4;
  color: #4285f4;
}
.map-button.google:hover {
  background: #4285f4;
  color: white;
}

/* 하단 액션 */
.bottom-actions {
  display: flex;
  gap: 15px;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #f3f4f6;
}
.btn {
  flex: 1;
  padding: 16px;
  border-radius: 10px;
  font-weight: 700;
  border: none;
  cursor: pointer;
}
.btn-primary {
  background: #6366f1;
  color: white;
}
.btn-secondary {
  background: white;
  color: #6366f1;
  border: 2px solid #6366f1;
}

/* FAQ 전체 영역 */
.faq-area {
  max-width: 900px;
  margin: 60px auto;
  padding: 0 20px;
  font-family: 'Noto Sans KR', 'Noto Sans Korean', sans-serif;
}

/* FAQ 타이틀 */
.faq-area .title {
  text-align: center;
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 32px;
  color: #222;
}

/* 리스트 초기화 */
.faq-list-element {
  margin: 0;
  padding: 0;
}

/* 각 FAQ 블록 */
.faq-list-cont {
  border-bottom: 1px solid #e5e7eb;
}

/* 질문 영역 */
.faq-q a {
  display: block;
  text-decoration: none;
  color: inherit;
}

/* 질문 박스 */
.vm-box {
  padding: 20px 12px;
}

/* 질문 내부 정렬 */
.vm-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

/* 질문 텍스트 */
.text-cont {
  font-size: 16px;
  font-weight: 600;
  color: #111;
  line-height: 1.5;
}

/* 화살표 아이콘 */
.ion-chevron-down {
  font-size: 18px;
  color: #6b7280;
  transition: transform 0.3s ease;
}

/* hover 효과 */
.faq-q a:hover .text-cont {
  color: #2563eb;
}

/* 답변 영역 */
.faq-a {
  display: none;
  padding: 0 12px 20px;
}

/* 답변 텍스트 */
.faq-a div {
  font-size: 15px;
  line-height: 1.7;
  color: #444;
  background: #f9fafb;
  padding: 16px;
  border-radius: 10px;
}

/* 열렸을 때 (JS로 faq-list-cont에 active 클래스 추가) */
.faq-list-cont.active .faq-a {
  display: block;
}

.faq-list-cont.active .ion-chevron-down {
  transform: rotate(180deg);
}

:deep(.faq-area) {
  max-width: 900px;
  margin: 60px auto;
}

:deep(.faq-area .title) {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 10px;
}

:deep(.faq-area .title span) {
  font-size: 24px !important;
  font-weight: 700;
}

:deep(.faq-list-cont) {
  border-bottom: 1px solid #e5e7eb;
}

:deep(.faq-a div) {
  background: #f9fafb;
  padding: 16px;
  border-radius: 10px;
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .faq-area {
    margin: 40px auto;
  }

  .text-cont {
    font-size: 15px;
  }

  .faq-a div {
    font-size: 14px;
  }
}

/* 로딩 & 스피너 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 20px;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #6366f1;
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
  .content-wrapper {
    padding: 20px;
  }
  .image-slider {
    margin: 20px -20px;
  }
  .slider-container {
    height: 300px;
  }
  .title {
    font-size: 2rem;
  }
  .location-actions,
  .bottom-actions {
    flex-direction: column;
  }
}
</style>
