import axiosInstance from './axios'

export const authAPI = {
  // 회원가입
  signup: async (userData) => {
    try {
      console.log('회원가입 요청 데이터:', userData)
      
      const response = await axiosInstance.post('/auth/signup/', userData)
      
      console.log('회원가입 성공:', response.data)
      
      if (response.data.token) {
        localStorage.setItem('access_token', response.data.token.access)
        localStorage.setItem('refresh_token', response.data.token.refresh)
      }
      
      return response.data
    } catch (error) {
      // 에러 상세 로깅
      console.error('회원가입 실패:', error.response?.data)
      throw error
    }
  },

 // 로그인
  login: async (credentials) => {
    try {
      console.log('로그인 요청:', { username: credentials.username })
      
      const response = await axiosInstance.post('/auth/login/', credentials)
      
      console.log('로그인 응답:', response.data)
      
      // 토큰 저장
      if (response.data.token) {
        localStorage.setItem('access_token', response.data.token.access)
        localStorage.setItem('refresh_token', response.data.token.refresh)
        
        console.log('토큰 저장 완료:', {
          access: response.data.token.access.substring(0, 20) + '...',
          refresh: response.data.token.refresh.substring(0, 20) + '...'
        })
      } else {
        console.warn('응답에 토큰이 없음!')
      }
      
      return response.data
    } catch (error) {
      console.error('로그인 요청 실패:', error.response?.data)
      throw error
    }
  },

  // 로그아웃
  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    
    try {
      console.log('로그아웃 요청')
      
      await axiosInstance.post('/auth/logout/', {
        refresh: refreshToken
      })
      
      console.log('로그아웃 API 성공')
    } catch (error) {
      console.error('로그아웃 API 실패:', error)
    } finally {
      // 토큰 삭제는 항상 실행
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      console.log('토큰 삭제 완료')
    }
  },

  // 현재 사용자 정보
  getUserInfo: async () => {
    try {
      console.log('사용자 정보 요청')
      
      const response = await axiosInstance.get('/auth/user/')
      
      console.log('사용자 정보 응답:', response.data)
      
      return response.data
    } catch (error) {
      console.error('사용자 정보 요청 실패:', error.response?.status)
      throw error
    }
  },

  // 토큰 갱신
  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await axiosInstance.post('/auth/token/refresh/', {
      refresh: refreshToken
    })
    
    // 새 Access Token 저장
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access)
    }
    
    return response.data
  }
}