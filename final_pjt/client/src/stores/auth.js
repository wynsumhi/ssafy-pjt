import { authAPI } from '@/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 상태
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 로그인 여부 (토큰 존재 + user 정보)
  const isLoggedIn = computed(() => {
    const hasToken = !!localStorage.getItem('access_token')
    const hasUser = !!user.value
    
    console.log('isLoggedIn 계산:', { hasToken, hasUser, result: hasToken && hasUser })
    
    return hasToken && hasUser
  })

  const isAuthenticated = computed(() => isLoggedIn.value)

  // 사용자 정보 가져오기 (토큰이 있을 때만)
  const fetchUser = async () => {
    const token = localStorage.getItem('access_token')
    
    if (!token) {
      user.value = null
      return null
    }

    loading.value = true
    error.value = null
    
    try {
      const data = await authAPI.getUserInfo()
      user.value = data
      return data
    } catch (err) {
      console.error('사용자 정보 로딩 실패:', err)
      
      // 401 에러면 토큰 삭제
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        user.value = null
      }
      
      throw err
    } finally {
      loading.value = false
    }
  }

  // 카카오맵 호출 시 사용
  const checkAuth = async () => {
    try {
      await fetchUser()
      return true
    } catch (err) {
      return false
    }
  }

  // 로그인
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await authAPI.login(credentials)
      user.value = data.user
      return data
    } catch (err) {
      error.value = err.response?.data?.error || '로그인에 실패했습니다.'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 로그아웃
  const logout = async () => {
    loading.value = true
    
    try {
      await authAPI.logout()
    } catch (err) {
      console.error('로그아웃 실패:', err)
    } finally {
      user.value = null
      loading.value = false
    }
  }

  // 회원가입
  const signup = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await authAPI.signup(userData)
      user.value = data.user
      
      console.log('회원가입 성공:', {
      user: user.value,
      hasToken: !!localStorage.getItem('access_token')
    })
      return data
    } catch (err) {
      error.value = err.response?.data?.error || '회원가입에 실패했습니다.'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 상태
    user,
    loading,
    error,
    
    // Computed
    isLoggedIn,
    isAuthenticated,
    
    // 메서드
    fetchUser,
    checkAuth,
    login,
    logout,
    signup,
  }
})