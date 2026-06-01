import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'

// 전역 스타일
import '@/assets/styles/global.scss'

// Kakao Map API 동적 로드 함수
const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    // 이미 로드되어 있는지 확인
    if (window.kakao && window.kakao.maps) {
      console.log('Kakao Maps API 이미 로드됨')
      resolve()
      return
    }

    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_API_KEY}&autoload=false`
    script.async = true
    
    script.onload = () => {
      // autoload=false 옵션을 사용했으므로 수동으로 로드
      window.kakao.maps.load(() => {
        console.log('Kakao Maps API 로드 완료')
        resolve()
      })
    }
    
    script.onerror = () => {
      console.error('Kakao Maps API 로드 실패')
      reject(new Error('Kakao Maps API를 로드할 수 없습니다.'))
    }
    
    document.head.appendChild(script)
  })
}

// Kakao Map 로드 후 앱 실행
loadKakaoMapScript()
  .then(() => {
    const app = createApp(App)
    const pinia = createPinia()
    pinia.use(piniaPluginPersistedstate)

    app.use(pinia)
    app.use(router)

    app.mount('#app')
    
    console.log('앱 마운트 완료')
  })
  .catch((error) => {
    console.error('앱 초기화 실패:', error)
    alert('지도를 로드할 수 없습니다. 페이지를 새로고침해주세요.')
  })