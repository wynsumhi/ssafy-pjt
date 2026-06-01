<template>
  <div class="profile-edit">
    <div class="container">
      <div class="header-section">
        <button @click="$router.back()" class="btn-back">← 취소</button>
        <h1 class="page-title">프로필 수정</h1>
      </div>

      <div class="edit-card">
        <form @submit.prevent="handleSubmit">
          <div class="avatar-edit-section">
            <div class="avatar-preview">
              <img
                :src="previewImage || user.profile_image || defaultAvatar"
                alt="Profile Preview"
              />
            </div>
            <label for="file-upload" class="file-label">
              사진 변경
              <input
                id="file-upload"
                type="file"
                @change="handleFileChange"
                accept="image/*"
                hidden
              />
            </label>
          </div>

          <div class="form-group">
            <label>닉네임</label>
            <input
              v-model="user.nickname"
              type="text"
              placeholder="새로운 닉네임을 입력하세요"
              required
            />
          </div>

          <div class="form-group">
            <label>소개글</label>
            <textarea v-model="user.bio" rows="4" placeholder="자신을 소개해 주세요"></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="submitting">
              {{ submitting ? '저장 중...' : '변경사항 저장' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
axios.defaults.baseURL = 'http://localhost:8000/api/v1'

const router = useRouter()
const defaultAvatar = 'https://cdn-icons-png.flaticon.com/512/149/149071.png'

// 상태 관리
const user = ref({
  nickname: '',
  bio: '',
  profile_image: null,
})
const selectedFile = ref(null)
const previewImage = ref(null)
const submitting = ref(false)

// 기존 프로필 정보 로드
const fetchProfile = async () => {
  const token = localStorage.getItem('access_token')
  try {
    const response = await axios.get('/api/v1/mypage/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    user.value.nickname = response.data.nickname
    user.value.bio = response.data.bio
    user.value.profile_image = response.data.profile_image
  } catch (error) {
    console.error('프로필 로드 실패:', error)
  }
}

// 파일 선택 시 미리보기 처리
const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// 정보 수정 제출
const handleSubmit = async () => {
  submitting.value = true
  const token = localStorage.getItem('access_token')

  // 이미지가 포함될 수 있으므로 FormData 사용
  const formData = new FormData()
  formData.append('nickname', user.value.nickname)
  formData.append('bio', user.value.bio || '')
  if (selectedFile.value) {
    formData.append('profile_image', selectedFile.value)
  }

  try {
    await axios.patch('/mypage/profile/', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    })
    alert('프로필이 성공적으로 수정되었습니다.')
    router.push('/profile') // 프로필 페이지로 이동
  } catch (error) {
    console.error('프로필 수정 실패:', error)
    alert('수정 중 오류가 발생했습니다.')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-edit {
  min-height: 100vh;
  background: #f8f9fa;
  padding: 40px 20px;
}

.container {
  max-width: 600px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.btn-back {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 800;
}

.edit-card {
  background: white;
  padding: 40px;
  border-radius: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* 아바타 수정 */
.avatar-edit-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 15px;
  border: 4px solid #f0f0f0;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-label {
  background: #e6e7f3;
  color: #667eea;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.file-label:hover {
  background: #667eea;
  color: white;
}

/* 폼 스타일 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 700;
  margin-bottom: 8px;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-family: inherit;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-actions {
  margin-top: 40px;
}

.btn-save {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.3s;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .edit-card {
    padding: 25px;
  }
}
</style>
