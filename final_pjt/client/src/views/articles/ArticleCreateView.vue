<template>
  <div class="article-create-container">
    <div class="article-create-header">
      <h1>당신만의 지역 구석구석 경험을 공유해주세요</h1>
      <button @click="handleCancel" class="btn-cancel">취소</button>
    </div>

    <form @submit.prevent="handleSubmit" class="article-form">
      <!-- 장소 선택 -->
      <div class="form-group">
        <label for="place">장소 <span class="required">*</span></label>
        <select id="place" v-model="formData.place_id" required class="form-control">
          <option value="">장소를 선택하세요</option>
          <option v-for="place in places" :key="place.place_id" :value="place.place_id">
            {{ place.name }} - {{ place.category }}
          </option>
        </select>
      </div>

      <!-- 제목 -->
      <div class="form-group">
        <label for="title">제목 <span class="required">*</span></label>
        <input
          id="title"
          v-model="formData.title"
          type="text"
          maxlength="100"
          required
          placeholder="게시물 제목을 입력하세요"
          class="form-control"
        />
        <span class="char-count">{{ formData.title.length }}/100</span>
      </div>

      <!-- 내용 -->
      <div class="form-group">
        <label for="content">내용 <span class="required">*</span></label>
        <textarea
          id="content"
          v-model="formData.content"
          required
          placeholder="게시물 내용을 입력하세요"
          class="form-control"
          rows="10"
        ></textarea>
      </div>

      <!-- 해시태그 -->
      <div class="form-group">
        <label for="hashtags">해시태그</label>
        <input
          id="hashtags"
          v-model="hashtagInput"
          type="text"
          placeholder="#감성카페 #야장맛집 #길거리음식"
          class="form-control"
          @keypress.enter.prevent="addHashtag"
        />
        <div v-if="hashtags.length > 0" class="hashtag-list">
          <span v-for="(tag, index) in hashtags" :key="index" class="hashtag-item">
            {{ tag }}
            <button type="button" @click="removeHashtag(index)" class="btn-remove-tag">×</button>
          </span>
        </div>
      </div>

      <!-- 이미지 업로드 -->
      <div class="form-group">
        <label>이미지</label>
        <div class="image-upload-area">
          <input
            type="file"
            ref="fileInput"
            @change="handleFileChange"
            accept="image/*"
            multiple
            class="file-input"
          />
          <button type="button" @click="triggerFileInput" class="btn-upload">이미지 선택</button>
          <span class="upload-hint">최대 10개까지 업로드 가능</span>
        </div>

        <!-- 이미지 미리보기 -->
        <div v-if="imagePreview.length > 0" class="image-preview-list">
          <div v-for="(img, index) in imagePreview" :key="index" class="image-preview-item">
            <img :src="img.url" :alt="`preview-${index}`" />
            <button type="button" @click="removeImage(index)" class="btn-remove-image">×</button>
            <input
              v-model="img.order"
              type="number"
              min="0"
              class="image-order"
              placeholder="순서"
            />
          </div>
        </div>
      </div>

      <!-- 제출 버튼 -->
      <div class="form-actions">
        <button type="submit" class="btn-submit" :disabled="isSubmitting">
          {{ isSubmitting ? '작성 중...' : '게시물 작성' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isSubmitting = ref(false)
const fileInput = ref(null)
const places = ref([])

const formData = reactive({
  place_id: '',
  title: '',
  content: '',
})

const hashtagInput = ref('')
const hashtags = ref([])
const imagePreview = ref([])
const imageFiles = ref([])

// 장소 목록 불러오기
const fetchPlaces = async () => {
  try {
    const response = await fetch('/api/places')
    if (response.ok) {
      places.value = await response.json()
    }
  } catch (error) {
    console.error('장소 목록 로딩 실패:', error)
    alert('장소 목록을 불러오는데 실패했습니다.')
  }
}

// 해시태그 추가
const addHashtag = () => {
  const tags = hashtagInput.value
    .split(' ')
    .filter((tag) => tag.trim().startsWith('#'))
    .map((tag) => tag.trim())

  hashtags.value = [...new Set([...hashtags.value, ...tags])]
  hashtagInput.value = ''
}

// 해시태그 제거
const removeHashtag = (index) => {
  hashtags.value.splice(index, 1)
}

// 파일 입력 트리거
const triggerFileInput = () => {
  fileInput.value.click()
}

// 파일 선택 처리
const handleFileChange = (event) => {
  const files = Array.from(event.target.files)

  if (imagePreview.value.length + files.length > 10) {
    alert('이미지는 최대 10개까지 업로드 가능합니다.')
    return
  }

  files.forEach((file, index) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        imagePreview.value.push({
          url: e.target.result,
          order: imagePreview.value.length,
          file: file,
        })
        imageFiles.value.push(file)
      }
      reader.readAsDataURL(file)
    }
  })

  event.target.value = ''
}

// 이미지 제거
const removeImage = (index) => {
  imagePreview.value.splice(index, 1)
  imageFiles.value.splice(index, 1)
}

// 폼 제출
const handleSubmit = async () => {
  if (isSubmitting.value) return

  isSubmitting.value = true

  try {
    // FormData 생성
    const formDataToSend = new FormData()
    formDataToSend.append('place_id', formData.place_id)
    formDataToSend.append('title', formData.title)
    formDataToSend.append('content', formData.content)
    formDataToSend.append('hashtags', hashtags.value.join(' '))

    // 이미지 추가 (순서와 함께)
    imagePreview.value.forEach((img, index) => {
      formDataToSend.append('images', img.file)
      formDataToSend.append(`image_order_${index}`, img.order)
    })

    const response = await fetch('/api/articles', {
      method: 'POST',
      body: formDataToSend,
    })

    if (response.ok) {
      const data = await response.json()
      alert('게시물이 작성되었습니다.')
      router.push(`/articles/${data.article_id}`)
    } else {
      const error = await response.json()
      alert(error.message || '게시물 작성에 실패했습니다.')
    }
  } catch (error) {
    console.error('게시물 작성 오류:', error)
    alert('게시물 작성 중 오류가 발생했습니다.')
  } finally {
    isSubmitting.value = false
  }
}

// 취소
const handleCancel = () => {
  if (confirm('작성을 취소하시겠습니까? 작성 중인 내용이 사라집니다.')) {
    router.back()
  }
}

onMounted(() => {
  fetchPlaces()
})
</script>

<style scoped>
.article-create-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.article-create-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.article-create-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.article-form {
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.required {
  color: #ff4757;
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

textarea.form-control {
  resize: vertical;
  min-height: 200px;
  font-family: inherit;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.hashtag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.hashtag-item {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  font-size: 14px;
  gap: 6px;
}

.btn-remove-tag {
  background: none;
  border: none;
  color: #1976d2;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.btn-remove-tag:hover {
  color: #0d47a1;
}

.image-upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-input {
  display: none;
}

.btn-upload {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.3s;
}

.btn-upload:hover {
  background: #2980b9;
}

.upload-hint {
  font-size: 12px;
  color: #999;
}

.image-preview-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #eee;
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.btn-remove-image:hover {
  background: rgba(255, 0, 0, 0.8);
}

.image-order {
  position: absolute;
  bottom: 8px;
  left: 8px;
  width: 50px;
  padding: 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  text-align: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn-submit {
  padding: 12px 32px;
  background: #2ecc71;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-submit:hover:not(:disabled) {
  background: #27ae60;
}

.btn-submit:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-cancel {
  padding: 8px 20px;
  background: transparent;
  color: #7f8c8d;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: #f8f9fa;
  border-color: #bdc3c7;
}
</style>