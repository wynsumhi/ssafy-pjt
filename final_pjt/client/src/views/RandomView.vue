<template>
  <div class="main-view">
    <div class="content-container">
      <!-- 좌측: 지도 영역 -->
      <div class="map-section">
        <!-- 위치 로딩 중 표시 -->
        <div v-if="isLoadingLocation" class="loading-overlay">
          <div class="loading-content">
            <div class="spinner">📍</div>
            <p>현재 위치를 가져오는 중...</p>
            <button @click="useDefaultLocation" class="skip-btn">기본 위치로 시작하기</button>
          </div>
        </div>

        <!-- 카카오맵 컴포넌트 -->
        <KakaoMap
          v-if="currentPosition.lat && currentPosition.lng && !isLoadingLocation"
          ref="mapRef"
          :latitude="selectedArticle ? selectedArticle.place.lat : currentPosition.lat"
          :longitude="selectedArticle ? selectedArticle.place.lng : currentPosition.lng"
          :level="selectedArticle ? 3 : mapLevel"
          :markers="selectedArticle ? [selectedArticle.place] : []"
          @marker-click="handleMarkerClick"
        />

        <!-- 현재 위치 버튼 -->
        <button
          v-if="!isLoadingLocation"
          @click="getCurrentLocation"
          class="current-location-btn"
          title="현재 위치로 이동"
        >
          📍
        </button>

        <!-- 위치 정보 표시 -->
        <div v-if="!isLoadingLocation && !selectedArticle" class="location-badge">
          <span v-if="locationMethod === 'gps'">📍 GPS 위치</span>
          <span v-else>🏢 역삼역 멀티캠퍼스</span>
        </div>

        <!-- 가챠 결과 - 게시글 카드 -->
        <div v-if="selectedArticle" class="article-card">
          <div class="article-header">
            <h3>🎉 오늘의 추천깡!</h3>
          </div>
          <div class="article-content">
            <!-- 게시글 이미지 -->
            <div
              class="article-image"
              v-if="selectedArticle.images && selectedArticle.images.length > 0"
            >
              <img :src="selectedArticle.images[0]" :alt="selectedArticle.title" />
            </div>

            <!-- 게시글 정보 -->
            <div class="article-info">
              <h2>{{ selectedArticle.title }}</h2>
              <p class="article-author">
                <span class="author-icon">👤</span>
                {{ selectedArticle.author }}
              </p>
              <p class="article-place">
                <span class="place-icon">📍</span>
                {{ selectedArticle.place.title }}
              </p>
              <p class="article-preview">{{ selectedArticle.content }}</p>

              <div class="article-meta">
                <span class="article-rating">⭐ {{ selectedArticle.rating }}</span>
                <span class="article-date">{{ selectedArticle.createdAt }}</span>
              </div>
            </div>

            <!-- 액션 버튼 -->
            <div class="article-actions">
              <button @click="goToArticleDetail" class="detail-btn">게시글 보기</button>
              <button @click="resetGacha" class="retry-btn">다시 뽑기</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 우측: 필터 & 랜덤깡 영역 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h1 class="title">오늘은 어디로 갈까요?</h1>
          <p class="subtitle">필터를 선택하고 랜덤으로 뽑아보세요!</p>
          <button @click="handleGacha" class="gacha-button" :disabled="isSpinning">
            <span class="button-icon">{{ isSpinning ? '🎰' : '🎲' }}</span>
            <span class="button-text">{{ isSpinning ? ' 뽑는 중...' : ' 랜덤깡!' }}</span>
          </button>
        </div>

        <div class="sidebar-scroll-area">
          <div class="filter-section">
            <div class="filter-group">
              <div class="group-header">
                <h3>카테고리</h3>
                <span class="selection-info">최대 3개</span>
              </div>
              <div class="category-chips">
                <button
                  v-for="category in categories"
                  :key="category.id"
                  @click="toggleCategory(category.id)"
                  :class="['category-chip', { active: selectedCategories.includes(category.id) }]"
                >
                  {{ category.icon }} {{ category.name }}
                </button>
              </div>
            </div>

            <div class="filter-group">
              <h3>거리 설정</h3>
              <div class="distance-options">
                <button
                  v-for="option in distanceOptions"
                  :key="option.id"
                  @click="selectedDistance = option.id"
                  :class="['distance-option', { active: selectedDistance === option.id }]"
                >
                  <span class="option-icon">{{ option.icon }}</span>
                  <span class="option-label">{{ option.label }}</span>
                </button>
              </div>
            </div>

            <button @click="resetFilters" class="reset-btn">필터 초기화</button>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import KakaoMap from '../components/KakaoMap.vue'

const router = useRouter()
const mapRef = ref(null)
const mapLevel = ref(5)
const isSpinning = ref(false)
const selectedCategories = ref(['all'])
const selectedDistance = ref('5km') // 기본값: 5km
const isLoadingLocation = ref(true)
const locationMethod = ref('default')
const selectedArticle = ref(null)
const allArticles = ref([]) // 전체 게시글 캐시
const isLoadingArticles = ref(false) // 게시글 로딩 상태

// 현재 위치 (기본값: 역삼역 멀티캠퍼스)
const currentPosition = ref({
  lat: 37.5012767241426,
  lng: 127.03958123605,
})

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// 거리 옵션 (5단계)
const distanceOptions = [
  { id: '1km', label: '1km', value: 1, icon: '🎯' },
  { id: '3km', label: '3km', value: 3, icon: '🚶' },
  { id: '5km', label: '5km', value: 5, icon: '🚴' },
  { id: '10km', label: '10km', value: 10, icon: '🚗' },
  { id: 'all', label: '전체', value: null, icon: '🌍' },
]

// 카테고리 목록 (백엔드 category_path와 매칭)
const categories = ref([
  { id: 'all', name: '전체', icon: '🎲', apiValue: null },
  { id: 'restaurant', name: '음식점', icon: '🍽️', apiValue: '음식' },
  { id: 'cafe', name: '카페', icon: '☕', apiValue: '카페' },
  { id: 'shopping', name: '쇼핑', icon: '🛍️', apiValue: '쇼핑' },
  { id: 'culture', name: '문화시설', icon: '🎨', apiValue: '문화시설' },
  { id: 'experience', name: '체험관광', icon: '🎯', apiValue: '체험' },
  { id: 'accommodation', name: '숙박', icon: '🏨', apiValue: '숙박' },
  { id: 'nature', name: '자연 명소', icon: '🌳', apiValue: '자연' },
  { id: 'festival', name: '축제 행사 공연', icon: '🎪', apiValue: '축제' },
  { id: 'historic', name: '역사 유적지', icon: '🏛️', apiValue: '역사' },
])

// Axios 인스턴스 생성
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터: 토큰 자동 추가
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 응답 인터셉터: 에러 처리
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 401 에러이고 재시도하지 않은 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          })

          const newAccessToken = response.data.access
          localStorage.setItem('access_token', newAccessToken)

          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return axiosInstance(originalRequest)
        }
      } catch (refreshError) {
        // 토큰 갱신 실패 시 로그인 페이지로 이동
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

// Haversine 공식을 사용한 거리 계산 (km 단위)
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371 // 지구 반경 (km)

  const lat1Rad = (lat1 * Math.PI) / 180
  const lat2Rad = (lat2 * Math.PI) / 180
  const deltaLat = ((lat2 - lat1) * Math.PI) / 180
  const deltaLon = ((lon2 - lon1) * Math.PI) / 180

  const a =
    Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
    Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2)

  const c = 2 * Math.asin(Math.sqrt(a))

  return R * c
}

// Haversine 역함수: 특정 거리 내의 위도/경도 범위 계산
const getBoundingBox = (centerLat, centerLon, radiusKm) => {
  const R = 6371 // 지구 반경 (km)

  // 위도 1도당 거리 (약 111km)
  const latDelta = radiusKm / 111.0

  // 경도 1도당 거리는 위도에 따라 변함 (위도가 높을수록 짧아짐)
  const lonDelta = radiusKm / (111.0 * Math.cos((centerLat * Math.PI) / 180))

  return {
    minLat: centerLat - latDelta,
    maxLat: centerLat + latDelta,
    minLon: centerLon - lonDelta,
    maxLon: centerLon + lonDelta,
  }
}

// 위도/경도 범위 내에 있는지 빠르게 체크
const isInBoundingBox = (lat, lon, boundingBox) => {
  return (
    lat >= boundingBox.minLat &&
    lat <= boundingBox.maxLat &&
    lon >= boundingBox.minLon &&
    lon <= boundingBox.maxLon
  )
}

// 필터링된 게시글 목록 계산 (캐시된 데이터 사용 + 최적화)
const filteredArticles = computed(() => {
  if (!allArticles.value.length) {
    return []
  }

  let result = [...allArticles.value]

  // 1. 카테고리 필터 (먼저 적용하여 데이터셋 축소)
  if (selectedCategories.value.length > 0 && !selectedCategories.value.includes('all')) {
    const selectedApiValues = selectedCategories.value
      .map((id) => categories.value.find((cat) => cat.id === id)?.apiValue)
      .filter(Boolean)

    result = result.filter((article) => {
      if (!article.place?.category_path) return false
      return selectedApiValues.some((apiValue) => article.place.category_path.includes(apiValue))
    })
  }

  // 2. 거리 필터 (Bounding Box 최적화)
  const distanceOption = distanceOptions.find((opt) => opt.id === selectedDistance.value)
  const maxDistance = distanceOption?.value

  if (maxDistance !== null) {
    // Bounding Box 계산 (사각형 범위)
    const boundingBox = getBoundingBox(
      currentPosition.value.lat,
      currentPosition.value.lng,
      maxDistance,
    )

    console.log('📦 Bounding Box:', boundingBox)

    // Step 1: Bounding Box로 빠른 1차 필터링
    result = result.filter((article) => {
      if (!article.place?.latitude || !article.place?.longitude) return false

      const lat = parseFloat(article.place.latitude)
      const lon = parseFloat(article.place.longitude)

      return isInBoundingBox(lat, lon, boundingBox)
    })

    console.log(`📍 Bounding Box 1차 필터링: ${result.length}개`)

    // Step 2: 정확한 거리 계산 (1차 필터링된 것만)
    result = result
      .map((article) => {
        const distance = calculateDistance(
          currentPosition.value.lat,
          currentPosition.value.lng,
          parseFloat(article.place.latitude),
          parseFloat(article.place.longitude),
        )
        return { ...article, distance }
      })
      .filter((article) => article.distance <= maxDistance)

    console.log(`🎯 정확한 거리 2차 필터링: ${result.length}개`)
  } else {
    // 거리 제한 없음 (전체) - 거리만 계산
    result = result
      .map((article) => {
        if (!article.place?.latitude || !article.place?.longitude) {
          return { ...article, distance: null }
        }

        const distance = calculateDistance(
          currentPosition.value.lat,
          currentPosition.value.lng,
          parseFloat(article.place.latitude),
          parseFloat(article.place.longitude),
        )

        return { ...article, distance }
      })
      .filter((article) => article.distance !== null)
  }

  // 3. 거리순으로 정렬
  result.sort((a, b) => a.distance - b.distance)

  console.log(`✅ 최종 필터링 결과: ${result.length}개`)

  return result
})

// 전체 게시글 목록 가져오기 (캐싱)
const fetchAllArticles = async () => {
  if (allArticles.value.length > 0) {
    console.log('📦 캐시된 게시글 사용:', allArticles.value.length, '개')
    return
  }

  isLoadingArticles.value = true

  try {
    console.log('🔄 게시글 목록 로딩 중...')

    // TODO: 실제 API 엔드포인트로 교체 필요
    // GET /api/v1/articles/?page_size=1000&is_published=true
    const response = await axiosInstance.get('/articles/', {
      params: {
        page_size: 1000,
        is_published: true,
      },
    })

    allArticles.value = response.data.results || []

    console.log('✅ 게시글 로딩 완료:', allArticles.value.length, '개')
  } catch (error) {
    console.error('❌ 게시글 로딩 실패:', error)

    // 에러 시 빈 배열 유지
    allArticles.value = []

    // 인증 에러가 아닌 경우에만 알림
    if (error.response?.status !== 401) {
      console.warn('게시글을 불러올 수 없습니다. 뽑기 기능은 정상 작동합니다.')
    }
  } finally {
    isLoadingArticles.value = false
  }
}

// 필터링된 게시글 개수 표시용 computed

// 자동으로 현재 위치 가져오기
const tryGetCurrentLocation = () => {
  console.log('현재 위치 가져오기 시도!')

  if (!navigator.geolocation) {
    console.log('Geolocation 미지원, 기본 위치 사용')
    useDefaultLocation()
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      console.log('위치 가져오기 성공:', position.coords)
      currentPosition.value = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      }
      locationMethod.value = 'gps'
      isLoadingLocation.value = false

      // 위치를 가져온 후 게시글 목록 로딩
      fetchAllArticles()
    },
    (error) => {
      console.log('위치 가져오기 실패:', error.message)
      useDefaultLocation()
    },
    {
      enableHighAccuracy: false,
      timeout: 5000,
      maximumAge: 300000,
    },
  )
}

// 기본 위치 사용 (역삼역 멀티캠퍼스)
const useDefaultLocation = () => {
  console.log('기본 위치 사용 (역삼역 멀티캠퍼스)')
  currentPosition.value = {
    lat: 37.5012767241426,
    lng: 127.03958123605,
  }
  locationMethod.value = 'default'
  isLoadingLocation.value = false

  // 기본 위치 설정 후 게시글 목록 로딩
  fetchAllArticles()
}

// 현재 위치 버튼 클릭 시
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    alert('이 브라우저는 위치 정보를 지원하지 않습니다.')
    return
  }

  isLoadingLocation.value = true

  navigator.geolocation.getCurrentPosition(
    (position) => {
      currentPosition.value = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      }
      locationMethod.value = 'gps'
      isLoadingLocation.value = false

      if (!selectedArticle.value) {
        mapRef.value?.setCenter(currentPosition.value.lat, currentPosition.value.lng)
      }

      // 위치 변경 시 게시글이 없으면 로딩
      if (allArticles.value.length === 0) {
        fetchAllArticles()
      }
    },
    (error) => {
      console.error('위치 정보 가져오기 실패:', error.message)
      isLoadingLocation.value = false
      alert('위치 정보를 가져올 수 없습니다.\n브라우저 설정에서 위치 권한을 확인해주세요.')
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    },
  )
}

// 카테고리 토글
const toggleCategory = (categoryId) => {
  if (categoryId === 'all') {
    selectedCategories.value = ['all']
    return
  }

  if (selectedCategories.value.includes('all')) {
    selectedCategories.value = [categoryId]
    return
  }

  const index = selectedCategories.value.indexOf(categoryId)

  if (index > -1) {
    if (selectedCategories.value.length > 1) {
      selectedCategories.value.splice(index, 1)
    }
  } else {
    if (selectedCategories.value.length < 3) {
      selectedCategories.value.push(categoryId)
    } else {
      alert('카테고리는 최대 3개까지 선택할 수 있습니다!')
    }
  }
}

// 필터 초기화
const resetFilters = () => {
  selectedDistance.value = '5km'
  selectedCategories.value = ['all']
}

// 마커 클릭 핸들러
const handleMarkerClick = (place) => {
  console.log('마커 클릭:', place)
}

// 랜덤깡 (API 연동 + 로컬 필터링 체크)
const handleGacha = async () => {
  // 로그인 체크
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('로그인이 필요한 서비스입니다.')
    router.push('/login')
    return
  }

  // 로컬 필터링 결과 체크
  if (allArticles.value.length > 0 && filteredArticles.value.length === 0) {
    alert('선택한 조건에 맞는 게시글이 없습니다!\n필터를 조정해주세요.')
    return
  }

  isSpinning.value = true
  selectedArticle.value = null

  try {
    // 선택된 카테고리의 API 값 추출
    const selectedCategoryApiValues = selectedCategories.value
      .filter((id) => id !== 'all')
      .map((id) => categories.value.find((cat) => cat.id === id)?.apiValue)
      .filter(Boolean)

    // 거리 옵션에서 실제 값 추출
    const distanceOption = distanceOptions.find((opt) => opt.id === selectedDistance.value)
    const maxDistance = distanceOption?.value

    // API 요청 데이터 구성
    const requestData = {
      lat: currentPosition.value.lat,
      lng: currentPosition.value.lng,
      categories: selectedCategoryApiValues.length > 0 ? selectedCategoryApiValues : undefined,
      max_distance: maxDistance,
      mode: 'ai', // 'random' 또는 'ai'
    }

    console.log('🎲 뽑기 API 요청:', requestData)
    console.log(`📊 로컬 필터링 결과: ${filteredArticles.value.length}개 매칭`)

    // API 호출
    const response = await axiosInstance.post('/draws/', requestData)

    console.log('✅ 뽑기 API 응답:', response.data)

    // 응답 데이터 파싱
    const articleData = response.data.article
    const distance = response.data.distance

    // 게시글 데이터 변환 (백엔드 응답 → 프론트엔드 형식)
    selectedArticle.value = {
      id: articleData.id,
      title: articleData.title,
      content: articleData.content,
      author: articleData.author?.nickname || 'AI 추천',
      rating: articleData.quality_score || 4.5,
      createdAt: new Date(articleData.created_at).toLocaleDateString('ko-KR'),
      images: articleData.images || [],
      place: {
        id: articleData.place.cid,
        title: articleData.place.title,
        category: articleData.place.category_path,
        address: articleData.place.address,
        lat: parseFloat(articleData.place.latitude),
        lng: parseFloat(articleData.place.longitude),
        distance: distance,
      },
    }

    console.log('🎰 선택된 게시글:', selectedArticle.value)

    // 지도 이동
    setTimeout(() => {
      if (selectedArticle.value?.place) {
        mapRef.value?.setCenter(selectedArticle.value.place.lat, selectedArticle.value.place.lng)
        mapRef.value?.setLevel(3)
      }
    }, 100)
  } catch (error) {
    console.error('❌ 뽑기 실패:', error)

    if (error.response?.status === 404) {
      alert('선택한 조건에 맞는 게시글이 없습니다.\n필터를 조정해주세요.')
    } else if (error.response?.status === 401) {
      alert('로그인이 만료되었습니다.\n다시 로그인해주세요.')
      router.push('/login')
    } else {
      alert('뽑기 중 오류가 발생했습니다.\n잠시 후 다시 시도해주세요.')
    }
  } finally {
    isSpinning.value = false
  }
}

// 가챠 초기화 (다시 뽑기)
const resetGacha = () => {
  selectedArticle.value = null
  mapRef.value?.setCenter(currentPosition.value.lat, currentPosition.value.lng)
  mapRef.value?.setLevel(5)
}

// 게시글 상세 페이지로 이동
const goToArticleDetail = () => {
  if (selectedArticle.value) {
    router.push(`/articles/${selectedArticle.value.id}`)
  }
}

onMounted(() => {
  console.log('RandomView 마운트됨')
  tryGetCurrentLocation()
})
</script>

<style scoped>
/* 최상위 레이아웃 */
.main-view {
  width: 100%;
  height: 94vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-container {
  display: flex;
  flex: 1;
  height: 100%;
  overflow: hidden;
}

/* 지도 영역 */
.map-section {
  flex: 1;
  position: relative;
  height: 100%;
}

/* 위치 로딩 오버레이 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  color: white;
}

.spinner {
  font-size: 4rem;
  animation: pulse 1.5s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

.loading-content p {
  font-size: 1.2rem;
  margin-bottom: 20px;
  font-weight: 600;
}

.skip-btn {
  padding: 12px 30px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
}

.skip-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
}

/* 현재 위치 버튼 */
.current-location-btn {
  position: absolute;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: white;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s;
  z-index: 10;
}

.current-location-btn:hover {
  transform: scale(1.1);
}

.current-location-btn:active {
  transform: scale(0.95);
}

/* 위치 배지 */
.location-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  background: white;
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.location-badge span {
  color: #667eea;
}

/* 게시글 카드 */
.article-card {
  position: absolute;
  bottom: 30px;
  left: 30px;
  right: 30px;
  max-width: 500px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  z-index: 10;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.article-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px 20px;
  text-align: center;
}

.article-header h3 {
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
}

.article-content {
  padding: 20px;
}

.article-image {
  width: 100%;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 15px;
}

.article-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.article-info h2 {
  font-size: 1.3rem;
  font-weight: 800;
  color: #333;
  margin-bottom: 10px;
  line-height: 1.4;
}

.article-author,
.article-place {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.author-icon,
.place-icon {
  font-size: 0.85rem;
}

.article-place {
  color: #667eea;
  font-weight: 600;
}

.article-preview {
  font-size: 0.95rem;
  color: #555;
  line-height: 1.6;
  margin: 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #999;
  margin-bottom: 15px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.article-rating {
  color: #ffa500;
  font-weight: 600;
}

.article-actions {
  display: flex;
  gap: 10px;
}

.detail-btn,
.retry-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.detail-btn {
  background: #667eea;
  color: white;
}

.detail-btn:hover {
  background: #5568d3;
  transform: translateY(-2px);
}

.retry-btn {
  background: #f5f5f5;
  color: #666;
}

.retry-btn:hover {
  background: #e0e0e0;
  color: #333;
}

/* 사이드바 */
.sidebar {
  width: 420px;
  background: white;
  display: flex;
  flex-direction: column;
  height: 100%;
  z-index: 100;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.15);
}

/* 사이드바 고정 헤더 */
.sidebar-header {
  padding: 40px 30px 30px;
  background: linear-gradient(145deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  flex-shrink: 0;
}

.title {
  font-size: 1.6rem;
  font-weight: 800;
  margin-bottom: 10px;
}
.subtitle {
  font-size: 0.9rem;
  opacity: 0.85;
  margin-bottom: 25px;
}

.sidebar-scroll-area {
  flex: 1;
  padding-bottom: 30px;
  overflow-y: auto;
}
.sidebar-scroll-area::-webkit-scrollbar {
  width: 6px;
}
.sidebar-scroll-area::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 10px;
}

/* 가챠 버튼 */
.gacha-button {
  padding: 15px 40px;
  font-size: 1.2rem;
  border-radius: 40px;
  background: white;
  color: #667eea;
  border: none;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.gacha-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.gacha-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.button-icon {
  font-size: 1.8rem;
}

.gacha-button:disabled .button-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 필터 섹션 */
.filter-section {
  padding: 30px;
}
.filter-group {
  margin-bottom: 35px;
}
.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.filter-group h3 {
  font-size: 1rem;
  color: #1a1a1a;
  font-weight: 800;
  margin: 0;
  margin-bottom: 15px;
}

.selection-info {
  font-size: 0.85rem;
  color: #999;
  font-weight: 500;
  margin-left: 8px;
}

.category-chips {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.category-chip {
  padding: 12px;
  border: 1px solid #eee;
  background: #fdfdfd;
  border-radius: 12px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  cursor: pointer;
}
.category-chip.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
}

/* 거리 옵션 버튼 */
.distance-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.distance-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #eee;
  background: #fdfdfd;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  font-weight: 500;
}

.distance-option:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.distance-option.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
}

.option-icon {
  font-size: 1.3rem;
}

.option-label {
  flex: 1;
  font-weight: 600;
}

.reset-btn {
  width: 100%;
  padding: 14px;
  background: #f5f5f5;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  color: #666;
  transition: all 0.3s;
  margin-top: 10px;
}

.reset-btn:hover {
  background: #e0e0e0;
  color: #333;
}

/* 정보 카드 */
.info-section {
  padding: 0 30px;
}
.info-card {
  background: #f8f9ff;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid #e0e6ff;
  text-align: center;
}
.info-label {
  font-size: 0.95rem;
  color: #666;
  font-weight: 600;
}
.info-value {
  font-size: 2.2rem;
  font-weight: 900;
  color: #667eea;
}
.info-value span {
  font-size: 1rem;
  color: #999;
  margin-left: 4px;
}

/* 태블릿 대응 (반응형) */
@media (max-width: 1024px) {
  .main-view {
    height: auto;
  }
  .content-container {
    flex-direction: column;
  }
  .map-section {
    height: 60%;
    flex: none;
  }
  .sidebar {
    width: 100%;
    height: 50%;
    box-shadow: 0 -10px 20px rgba(0, 0, 0, 0.05);
  }

  .sidebar-header {
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    text-align: left;
  }

  .title {
    margin-bottom: 0;
    font-size: 1.2rem;
  }
  .sidebar-header .subtitle {
    display: none;
  }
  .gacha-button {
    padding: 10px 20px;
    font-size: 1rem;
  }
  .category-chips {
    grid-template-columns: repeat(4, 1fr);
  }
  .article-card {
    max-width: 400px;
    bottom: 20px;
    left: 20px;
    right: 20px;
  }
}

@media (max-width: 768px) {
  .category-chips {
    grid-template-columns: repeat(3, 1fr);
  }
  .map-section {
    height: 45%;
  }
  .sidebar {
    height: 55%;
  }
}

/* 거리 설정 그룹 */
.filter-group h3 {
  font-size: 1rem;
  color: #1a1a1a;
  font-weight: 800;
  margin-bottom: 15px;
}

/* 5개가 한 줄에 꽉 차도록 설정 */
.distance-options {
  display: flex;
  flex-direction: row;
  gap: 5px;
  width: 100%;
}

/* 아이콘 없이 텍스트만 강조된 버튼 */
.distance-option {
  flex: 1;
  padding: 12px 0;
  border: 1px solid #eee;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 아이콘 숨김 처리 */
.option-icon {
  display: none;
}

/* 라벨 텍스트 스타일 */
.option-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #666;
}

/* 활성화 상태 (파란색 배경) */
.distance-option.active {
  background: #667eea;
  border-color: #667eea;
}

.distance-option.active .option-label {
  color: white;
}

/* 호버 효과 */
.distance-option:hover:not(.active) {
  background: #f5f5f5;
}
</style>
