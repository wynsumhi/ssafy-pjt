<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-box">
        <h1 class="title">로그인</h1>
        <p class="subtitle">지역 구석구석 새로운 경험을 시작하세요!</p>

        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="username">아이디</label>
            <input
              id="username"
              v-model="loginData.username"
              type="text"
              placeholder="아이디를 입력하세요"
              required
              autocomplete="username"
            />
          </div>

          <div class="form-group">
            <label for="password">비밀번호</label>
            <input
              id="password"
              v-model="loginData.password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              required
              autocomplete="current-password"
            />
          </div>

          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <button type="submit" class="submit-btn" :disabled="authStore.loading">
            {{ authStore.loading ? '로그인 중...' : '로그인' }}
          </button>
        </form>

        <div class="footer-text">
          <span>계정이 없으신가요?</span>
          <router-link to="/signup" class="link">회원가입</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginData = reactive({
  username: '',
  password: '',
})

const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''

  try {
    console.log('로그인 시도:', {
      username: loginData.username,
    })

    // 로그인 API 호출
    await authStore.login(loginData)

    console.log('로그인 성공!')
    console.log('User:', authStore.user)
    console.log('Token:', localStorage.getItem('access_token'))

    // 리다이렉트 경로 확인 후 이동
    const redirect = route.query.redirect || '/random'
    console.log(redirect, '로 이동 시도')
    
    await router.push(redirect)

  } catch (error) {
    console.error('로그인 실패:', error)

    // 에러 메시지 설정
    if (error.response?.status === 401) {
      errorMessage.value = '아이디 또는 비밀번호가 올바르지 않습니다.'
    } else if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error
    } else {
      errorMessage.value = '로그인에 실패했습니다. 다시 시도해주세요.'
    }
  }
}
</script>

<style scoped lang="scss">
.auth-page {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-container {
  width: 100%;
  max-width: 450px;
}

.auth-box {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

.title {
  font-size: 2rem;
  text-align: center;
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  label {
    font-weight: 500;
    color: #333;
  }

  input {
    padding: 0.875rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;

    &:focus {
      outline: none;
      border-color: #667eea;
    }
  }
}

.error-message {
  padding: 0.875rem;
  background-color: #fee;
  color: #c33;
  border-radius: 8px;
  font-size: 0.875rem;
  text-align: center;
}

.submit-btn {
  padding: 1rem;
  margin-top: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.footer-text {
  margin-top: 2rem;
  text-align: center;
  color: #666;

  span {
    margin-right: 0.5rem;
  }

  .link {
    color: #667eea;
    font-weight: 600;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

/* 반응형 */
@media (max-width: 768px) {
  .auth-page {
    padding: 1rem;
  }

  .auth-box {
    padding: 2rem 1.5rem;
  }

  .title {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 0.9rem;
  }
}
</style>