<template>
  <div class="article-edit-container">
    <div class="article-edit-header">
      <h1>게시물 수정</h1>
      <button @click="handleCancel" class="btn-cancel">취소</button>
    </div>

    <form @submit.prevent="handleSubmit" class="article-form">
      <!-- 장소 선택 -->
      <div class="form-group">
        <label for="place">장소 <span class="required">*</span></label>
        <select id="place" v-model="formData.place_id" required class="form-control">
          <option value="">장소를 선택하세요</option>
          <option v-for="place in places" :key="place.id" :value="place.id">
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

      <!-- 기존 이미지 관리 -->
      <div class="form-group">
        <label>기존 이미지</label>
        <div v-if="existingImages.length > 0" class="existing-images">
          <div
            v-for="(img, index) in existingImages"
            :key="img.id"
            :class="['existing-image-item', { deleted: img.toDelete }]"
          >
            <img :src="img.url" :alt="`existing-${index}`" />
            <button
              type="button"
              @click="toggleDeleteImage(index)"
              :class="['btn-toggle-delete', { active: img.toDelete }]"
            >
              {{ img.toDelete ? '복구' : '삭제' }}
            </button>
            <input
              v-model="img.order"
              type="number"
              min="0"
              class="image-order"
              placeholder="순서"
              :disabled="img.toDelete"
            />
          </div>
        </div>
        <p v-else class="no-images">기존 이미지가 없습니다</p>
      </div>

      <!-- 새 이미지 업로드 -->
      <div class="form-group">
        <label>새 이미지 추가</label>
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
          <span class="upload-hint"> 기존 이미지와 합쳐 최대 10개까지 가능 </span>
        </div>

        <!-- 새 이미지 미리보기 -->
        <div v-if="newImagePreview.length > 0" class="image-preview-list">
          <div v-for="(img, index) in newImagePreview" :key="index" class="image-preview-item">
            <img :src="img.url" :alt="`new-preview-${index}`" />
            <button type="button" @click="removeNewImage(index)" class="btn-remove-image">×</button>
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

      <!-- 수정 내역 -->
      <div class="form-group">
        <label class="info-label">
          <span class="info-icon">ℹ️</span>
          수정 시간이 게시물에 표시됩니다
        </label>
      </div>

      <!-- 제출 버튼 -->
      <div class="form-actions">
        <button type="submit" class="btn-submit" :disabled="isSubmitting">
          {{ isSubmitting ? '수정 중...' : '수정 완료' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isSubmitting = ref(false)
const fileInput = ref(null)

// 임시 장소 목록 데이터
const places = ref([
  { id: 1, name: '익선동 한옥마을', category: '역사 유적지' },
  { id: 2, name: '망원한강공원', category: '자연 명소' },
  { id: 3, name: '성수카페거리', category: '카페' },
  { id: 4, name: '북촌 한옥마을', category: '역사 유적지' },
  { id: 5, name: '여의도 한강공원', category: '자연 명소' },
  { id: 6, name: '홍대 맛집거리', category: '음식점' },
  { id: 7, name: '명동 쇼핑거리', category: '쇼핑' },
  { id: 8, name: '국립중앙박물관', category: '문화시설' },
])

// 임시 게시물 데이터 (기존 데이터)
const formData = reactive({
  place_id: 1,
  title: '익선동 한옥마을 방문 후기',
  content: `서울 종로구에 위치한 익선동 한옥마을은 1920-30년대 지어진 한옥들이 밀집된 지역입니다.

최근 몇 년 사이 젊은 상인들이 한옥을 개조하여 카페, 음식점, 잡화점 등을 운영하면서 서울의 핫플레이스로 자리잡았습니다.

좁은 골목길을 따라 걷다보면 전통 한옥의 아름다움과 현대적인 감각이 조화를 이루는 독특한 풍경을 만날 수 있습니다.

주말에는 많은 인파로 붐비니 평일 오후 방문을 추천드립니다!`,
})

const hashtagInput = ref('')
const hashtags = ref(['#익선동', '#한옥마을', '#서울여행', '#전통과현대'])

// 기존 이미지 (임시 데이터)
const existingImages = ref([
  {
    id: 1,
    url: 'https://via.placeholder.com/300x300/667eea/ffffff?text=익선동1',
    order: 0,
    toDelete: false,
  },
  {
    id: 2,
    url: 'https://via.placeholder.com/300x300/764ba2/ffffff?text=익선동2',
    order: 1,
    toDelete: false,
  },
  {
    id: 3,
    url: 'https://via.placeholder.com/300x300/f093fb/ffffff?text=익선동3',
    order: 2,
    toDelete: false,
  },
])

const newImagePreview = ref([])
const newImageFiles = ref([])

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

// 기존 이미지 삭제 토글
const toggleDeleteImage = (index) => {
  existingImages.value[index].toDelete = !existingImages.value[index].toDelete
}

// 파일 입력 트리거
const triggerFileInput = () => {
  fileInput.value.click()
}

// 파일 선택 처리
const handleFileChange = (event) => {
  const files = Array.from(event.target.files)

  const activeExistingCount = existingImages.value.filter((img) => !img.toDelete).length
  const totalCount = activeExistingCount + newImagePreview.value.length + files.length

  if (totalCount > 10) {
    alert('이미지는 최대 10개까지 업로드 가능합니다.')
    return
  }

  files.forEach((file) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        newImagePreview.value.push({
          url: e.target.result,
          order: activeExistingCount + newImagePreview.value.length,
          file: file,
        })
        newImageFiles.value.push(file)
      }
      reader.readAsDataURL(file)
    }
  })

  event.target.value = ''
}

// 새 이미지 제거
const removeNewImage = (index) => {
  newImagePreview.value.splice(index, 1)
  newImageFiles.value.splice(index, 1)
}

// 폼 제출
const handleSubmit = async () => {
  if (isSubmitting.value) return

  isSubmitting.value = true

  // 임시로 콘솔에 출력
  console.log('수정할 데이터:', {
    place_id: formData.place_id,
    title: formData.title,
    content: formData.content,
    hashtags: hashtags.value.join(' '),
    existingImages: existingImages.value.filter((img) => !img.toDelete),
    deleteImages: existingImages.value.filter((img) => img.toDelete),
    newImages: newImagePreview.value,
  })

  // 실제 API 호출 시뮬레이션
  setTimeout(() => {
    alert('게시물이 수정되었습니다!')
    isSubmitting.value = false
    router.push(`/articles/${route.params.id}`)
  }, 1000)
}

// 취소
const handleCancel = () => {
  if (confirm('수정을 취소하시겠습니까? 변경사항이 저장되지 않습니다.')) {
    router.push(`/articles/${route.params.id}`)
  }
}

onMounted(() => {
  console.log('게시물 수정 페이지 - 임시 데이터 로드 완료')
})
</script>

<style scoped>
.article-edit-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.article-edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.article-edit-header h1 {
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
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

.existing-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.existing-image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #eee;
  transition: all 0.3s;
}

.existing-image-item.deleted {
  opacity: 0.4;
  border-color: #e74c3c;
}

.existing-image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-toggle-delete {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #e74c3c;
  border: 1px solid #e74c3c;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-toggle-delete:hover {
  background: #e74c3c;
  color: white;
}

.btn-toggle-delete.active {
  background: #e74c3c;
  color: white;
}

.no-images {
  color: #999;
  font-size: 14px;
  font-style: italic;
  padding: 20px;
  text-align: center;
  background: #f8f9fa;
  border-radius: 8px;
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
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.3s;
}

.btn-upload:hover {
  background: #5568d3;
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
  border: 2px solid #667eea;
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

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #e8f5e9;
  border-radius: 8px;
  color: #2e7d32;
  font-size: 14px;
  font-weight: normal;
}

.info-icon {
  font-size: 18px;
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
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-submit:hover:not(:disabled) {
  background: #5568d3;
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