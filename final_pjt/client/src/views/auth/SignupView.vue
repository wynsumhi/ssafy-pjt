<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-box">
        <h1 class="title">회원가입</h1>
        <p class="subtitle">지역 구석구석 새로운 경험을 시작하세요!</p>

        <form @submit.prevent="handleSignup" class="auth-form">
          <!-- 아이디 -->
          <div class="form-group">
            <label for="username">아이디 *</label>
            <input
              id="username"
              v-model="signupData.username"
              type="text"
              placeholder="영문, 숫자 조합 4-20자"
              required
              autocomplete="username"
            />
          </div>

          <!-- 이메일 -->
          <div class="form-group">
            <label for="email">이메일 *</label>
            <input
              id="email"
              v-model="signupData.email"
              type="email"
              placeholder="example@email.com"
              required
              autocomplete="email"
            />
          </div>

          <!-- 닉네임 -->
          <div class="form-group">
            <label for="nickname">닉네임 *</label>
            <input
              id="nickname"
              v-model="signupData.nickname"
              type="text"
              placeholder="2-10자 이내"
              required
            />
          </div>

          <!-- 비밀번호 -->
          <div class="form-group">
            <label for="password">비밀번호 *</label>
            <input
              id="password"
              v-model="signupData.password"
              type="password"
              placeholder="8자 이상"
              required
              autocomplete="new-password"
            />
          </div>

          <!-- 비밀번호 확인 -->
          <div class="form-group">
            <label for="password2">비밀번호 확인 *</label>
            <input
              id="password2"
              v-model="signupData.password2"
              type="password"
              placeholder="비밀번호 재입력"
              required
              autocomplete="new-password"
            />
          </div>

          <!-- 에러 메시지 -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <!-- 제출 버튼 -->
          <button type="submit" class="submit-btn" :disabled="authStore.loading">
            {{ authStore.loading ? '가입 중...' : '회원가입' }}
          </button>
        </form>

        <!-- 로그인 링크 -->
        <div class="footer-text">
          <span>이미 계정이 있으신가요?</span>
          <router-link to="/login" class="link">로그인</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const signupData = reactive({
  username: '',
  email: '',
  nickname: '',
  password: '',
  password2: '',
})

const errorMessage = ref('')

const handleSignup = async () => {
  errorMessage.value = ''

  // 유효성 검사
  if (signupData.password !== signupData.password2) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  if (signupData.password.length < 8) {
    errorMessage.value = '비밀번호는 8자 이상이어야 합니다.'
    return
  }

  try {
    console.log('회원가입 시도:', {
      username: signupData.username,
      email: signupData.email,
      nickname: signupData.nickname,
    })

    // 회원가입 API 호출
    await authStore.signup(signupData)

    console.log('회원가입 성공!')
    console.log('User:', authStore.user)
    console.log('Token:', localStorage.getItem('access_token'))

    // 성공 메시지
    alert('회원가입이 완료되었습니다!')

    // /random 페이지로 이동
    await router.push('/random')

  } catch (error) {
    console.error('회원가입 실패:', error)

    // 에러 메시지 파싱
    const errors = error.response?.data
    
    if (errors) {
      const errorMessages = []
      
      if (errors.username) {
        errorMessages.push(`아이디: ${errors.username.join(', ')}`)
      }
      if (errors.email) {
        errorMessages.push(`이메일: ${errors.email.join(', ')}`)
      }
      if (errors.nickname) {
        errorMessages.push(`닉네임: ${errors.nickname.join(', ')}`)
      }
      if (errors.password) {
        errorMessages.push(`비밀번호: ${errors.password.join(', ')}`)
      }
      
      errorMessage.value = errorMessages.join('\n') || '회원가입에 실패했습니다.'
    } else {
      errorMessage.value = '회원가입에 실패했습니다. 다시 시도해주세요.'
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
  max-width: 500px;
}

.auth-box {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
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
  gap: 1.25rem;
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
      border-color: #f5576c;
    }
  }
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.875rem;
  white-space: pre-line;
  text-align: center;
}

.submit-btn {
  padding: 1rem;
  margin-top: 1rem;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(245, 87, 108, 0.4);
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
    color: #f5576c;
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