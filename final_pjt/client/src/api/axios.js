import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
axiosInstance.interceptors.request.use(
  (config) => {
    // localStorage에서 Access Token 가져오기
    const accessToken = localStorage.getItem('access_token')
    
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
);

// 응답 인터셉터 (토큰 만료 시 갱신)
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 401 에러이고, 재시도하지 않은 요청인 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Refresh Token으로 새 Access Token 발급
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response = await axios.post(
          `${API_BASE_URL}/auth/token/refresh/`,
          { refresh: refreshToken }
        )

        const { access } = response.data
        
        // 새 Access Token 저장
        localStorage.setItem('access_token', access)

        // 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${access}`
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        // Refresh Token도 만료됨 → 로그아웃 처리
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default axiosInstance