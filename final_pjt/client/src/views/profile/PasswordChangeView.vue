<template>
  <div class="password-change">
    <div class="container">
      <div class="header-section">
        <button @click="$router.back()" class="btn-back">← 취소</button>
        <h1 class="page-title">비밀번호 변경</h1>
        <p class="page-subtitle">안전한 계정 관리를 위해 정기적으로 비밀번호를 변경해 주세요.</p>
      </div>

      <div class="edit-card">
        <form @submit.prevent="handlePasswordChange">
          <div class="form-group">
            <label for="current-password">현재 비밀번호</label>
            <input
              id="current-password"
              v-model="passwordData.current_password"
              type="password"
              placeholder="현재 비밀번호를 입력하세요"
              required
            />
          </div>

          <hr class="divider" />

          <div class="form-group">
            <label for="new-password">새 비밀번호</label>
            <input
              id="new-password"
              v-model="passwordData.new_password"
              type="password"
              placeholder="새 비밀번호 (8자 이상)"
              required
            />
          </div>

          <div class="form-group">
            <label for="new-password-confirm">새 비밀번호 확인</label>
            <input
              id="new-password-confirm"
              v-model="passwordData.new_password_confirm"
              type="password"
              placeholder="새 비밀번호를 한 번 더 입력하세요"
              required
            />
            <p v-if="passwordMismatch" class="error-text">새 비밀번호가 일치하지 않습니다.</p>
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn-save"
              :disabled="submitting || passwordMismatch || !isFormValid"
            >
              {{ submitting ? '변경 중...' : '비밀번호 변경하기' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
axios.defaults.baseURL = 'http://localhost:8000/api/v1'

const router = useRouter()

// 상태 관리
const passwordData = ref({
  current_password: '',
  new_password: '',
  new_password_confirm: '',
})
const submitting = ref(false)

// 비밀번호 일치 여부 확인 (Computed)
const passwordMismatch = computed(() => {
  const { new_password, new_password_confirm } = passwordData.value
  return new_password && new_password_confirm && new_password !== new_password_confirm
})

// 폼 유효성 검사
const isFormValid = computed(() => {
  return (
    passwordData.value.current_password.length > 0 &&
    passwordData.value.new_password.length >= 8 &&
    passwordData.value.new_password_confirm.length >= 8
  )
})

// 비밀번호 변경 요청
const handlePasswordChange = async () => {
  if (passwordMismatch.value) return

  submitting.value = true
  const token = localStorage.getItem('access_token')

  try {
    await axios.post('/mypage/password/', passwordData.value, {
      headers: { Authorization: `Bearer ${token}` },
    })

    alert('비밀번호가 성공적으로 변경되었습니다. 다시 로그인해 주세요.')

    // 비밀번호 변경 후 로그아웃 처리 (보안상 권장)
    localStorage.removeItem('access_token')
    delete axios.defaults.headers.common['Authorization']
    router.push('/login')
  } catch (error) {
    console.error('비밀번호 변경 실패:', error)
    if (error.response?.status === 400) {
      alert(
        error.response.data.message ||
          '현재 비밀번호가 일치하지 않거나 데이터가 올바르지 않습니다.',
      )
    } else {
      alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.password-change {
  min-height: 100vh;
  background: #f8f9fa;
  padding: 40px 20px;
}

.container {
  max-width: 500px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 30px;
}

.btn-back {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 10px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #777;
  font-size: 0.95rem;
  line-height: 1.4;
}

.edit-card {
  background: white;
  padding: 40px;
  border-radius: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.divider {
  border: 0;
  border-top: 1px solid #eee;
  margin: 25px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 700;
  margin-bottom: 8px;
  color: #333;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error-text {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 5px;
  font-weight: 500;
}

.form-actions {
  margin-top: 35px;
}

.btn-save {
  width: 100%;
  padding: 15px;
  background: #1a1a1a; /* 비밀번호 변경은 조금 더 무거운 톤으로 설정 */
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-save:hover:not(:disabled) {
  background: #333;
}

.btn-save:disabled {
  background: #ccc;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .edit-card {
    padding: 25px;
  }
}
</style>
