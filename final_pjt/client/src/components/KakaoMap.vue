<template>
  <div ref="mapContainer" class="kakao-map"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  latitude: {
    type: Number,
    required: true
  },
  longitude: {
    type: Number,
    required: true
  },
  level: {
    type: Number,
    default: 5
  },
  markers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['mapClick', 'markerClick'])

const mapContainer = ref(null)
let map = null
let markerObjects = []
let infowindows = []

onMounted(() => {
  console.log('KakaoMap 컴포넌트 마운트됨')
  initMap()
})

const initMap = () => {
  // Kakao Maps API 로드 확인
  if (!window.kakao || !window.kakao.maps) {
    console.error('Kakao Maps API가 로드되지 않았습니다.')
    console.log('index.html에 Kakao Maps 스크립트가 있는지 확인하세요.')
    
    // 재시도 로직
    let retryCount = 0
    const maxRetries = 10
    const checkInterval = setInterval(() => {
      retryCount++
      console.log(`Kakao Maps API 로드 대기 중... (${retryCount}/${maxRetries})`)
      
      if (window.kakao && window.kakao.maps) {
        console.log('Kakao Maps API 로드 완료!')
        clearInterval(checkInterval)
        createMap()
      } else if (retryCount >= maxRetries) {
        console.error('Kakao Maps API 로드 실패 - 최대 재시도 횟수 초과')
        clearInterval(checkInterval)
      }
    }, 100)
    
    return
  }

  createMap()
}

const createMap = () => {
  try {
    const container = mapContainer.value
    
    if (!container) {
      console.error('지도 컨테이너를 찾을 수 없습니다.')
      return
    }

    console.log('지도 생성 중', {
      latitude: props.latitude,
      longitude: props.longitude,
      level: props.level
    })

    const options = {
      center: new window.kakao.maps.LatLng(props.latitude, props.longitude),
      level: props.level
    }
    
    map = new window.kakao.maps.Map(container, options)
    console.log('지도 생성 완료!')
    
    // 지도 클릭 이벤트
    window.kakao.maps.event.addListener(map, 'click', (mouseEvent) => {
      const latlng = mouseEvent.latLng
      emit('mapClick', {
        latitude: latlng.getLat(),
        longitude: latlng.getLng()
      })
    })
    
    // 초기 마커 표시
    if (props.markers && props.markers.length > 0) {
      console.log('마커 표시', props.markers.length, '개')
      displayMarkers()
    }
  } catch (error) {
    console.error('지도 생성 중 오류:', error)
  }
}

const displayMarkers = () => {
  if (!map || !window.kakao) {
    console.warn('지도 또는 Kakao API가 준비되지 않음')
    return
  }
  
  // 기존 마커 및 인포윈도우 제거
  markerObjects.forEach(marker => marker.setMap(null))
  infowindows.forEach(infowindow => infowindow.close())
  markerObjects = []
  infowindows = []
  
  console.log('마커 업데이트:', props.markers.length, '개')
  
  // 새 마커 추가
  props.markers.forEach((markerData, index) => {
    try {
      const position = new window.kakao.maps.LatLng(
        markerData.lat,
        markerData.lng
      )
      
      // 마커 이미지 설정
      const imageSrc = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png'
      const imageSize = new window.kakao.maps.Size(24, 35)
      const markerImage = new window.kakao.maps.MarkerImage(imageSrc, imageSize)
      
      const marker = new window.kakao.maps.Marker({
        position: position,
        image: markerImage,
        title: markerData.title || ''
      })
      
      marker.setMap(map)
      
      // 인포윈도우 생성
      const infowindow = new window.kakao.maps.InfoWindow({
        content: `
          <div style="
            padding: 12px 15px;
            font-size: 13px;
            white-space: nowrap;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            max-width: 200px;
          ">
            <strong style="display: block; margin-bottom: 5px; color: #333;">
              ${markerData.title}
            </strong>
            <span style="color: #666; font-size: 12px;">
              ${markerData.category} · ${markerData.distance}km
            </span>
          </div>
        `,
        removable: true
      })
      
      // 마커 클릭 이벤트
      window.kakao.maps.event.addListener(marker, 'click', () => {
        // 다른 인포윈도우 닫기
        infowindows.forEach(iw => iw.close())
        
        // 현재 인포윈도우 열기
        infowindow.open(map, marker)
        
        emit('markerClick', markerData)
      })
      
      markerObjects.push(marker)
      infowindows.push(infowindow)
      
      console.log(`마커 ${index + 1} 생성 완료:`, markerData.title)
    } catch (error) {
      console.error(`마커 ${index + 1} 생성 실패:`, error)
    }
  })
}

// 중심 좌표 변경 감지
watch(() => [props.latitude, props.longitude], ([newLat, newLng]) => {
  console.log('지도 중심 이동:', { lat: newLat, lng: newLng })
  if (map) {
    const moveLatLon = new window.kakao.maps.LatLng(newLat, newLng)
    map.setCenter(moveLatLon)
  }
})

// 마커 변경 감지
watch(() => props.markers, (newMarkers) => {
  console.log('마커 변경 감지:', newMarkers.length, '개')
  if (map) {
    displayMarkers()
  }
}, { deep: true })

// 외부에서 호출 가능한 메서드
defineExpose({
  setCenter: (lat, lng) => {
    console.log('setCenter 호출:', { lat, lng })
    if (map) {
      const moveLatLon = new window.kakao.maps.LatLng(lat, lng)
      map.setCenter(moveLatLon)
    }
  },
  setLevel: (level) => {
    console.log('setLevel 호출:', level)
    if (map) {
      map.setLevel(level)
    }
  },
  panTo: (lat, lng) => {
    console.log('panTo 호출:', { lat, lng })
    if (map) {
      const moveLatLon = new window.kakao.maps.LatLng(lat, lng)
      map.panTo(moveLatLon)
    }
  }
})
</script>

<style scoped>
.kakao-map {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>