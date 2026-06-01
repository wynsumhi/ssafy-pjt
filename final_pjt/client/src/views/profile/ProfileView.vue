<template>
  <div class="mypage">
    <div class="container">
      <div class="profile-header">
        <div class="profile-card">
          <div class="avatar-section">
            <div class="avatar">
              <img
                v-if="user.profile_image"
                :src="user.profile_image"
                alt="profile"
                class="profile-img"
              />
              <span v-else>👤</span>
            </div>
            <router-link to="/profile/edit" class="change-avatar-btn">프로필 수정</router-link>
          </div>
          <div class="profile-info">
            <h1 class="username">{{ user.nickname || '지구깡 멤버' }}</h1>
            <p class="email">{{ user.bio || '나를 소개하는 글을 남겨보세요.' }}</p>
            <div class="stats">
              <div class="stat-item">
                <span class="stat-value">{{ user.article_count || 0 }}</span>
                <span class="stat-label">작성한 글</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ user.follower_count || 0 }}</span>
                <span class="stat-label">팔로워</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ user.following_count || 0 }}</span>
                <span class="stat-label">팔로잉</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <h2 class="section-title">내 활동</h2>
        <div class="card-grid">
          <router-link to="/profile/articles" class="activity-card">
            <div class="card-icon">📝</div>
            <h3>작성한 글</h3>
            <p>{{ user.article_count || 0 }}개의 소중한 기록</p>
            <div class="card-arrow">→</div>
          </router-link>

          <router-link to="/profile/favorites" class="activity-card">
            <div class="card-icon">⭐</div>
            <h3>저장한 장소</h3>
            <p>다시 가고 싶은 곳들</p>
            <div class="card-arrow">→</div>
          </router-link>

          <router-link to="/profile/liked-articles" class="activity-card">
            <div class="card-icon">✅</div>
            <h3>좋아요 목록</h3>
            <p>관심 있는 게시글</p>
            <div class="card-arrow">→</div>
          </router-link>
        </div>
      </div>

      <div class="section">
        <h2 class="section-title">계정 설정</h2>
        <div class="menu-list">
          <router-link to="/profile/edit" class="menu-item">
            <div class="menu-left">
              <span class="menu-icon">⚙️</span>
              <span>프로필 수정</span>
            </div>
            <span class="menu-arrow">›</span>
          </router-link>

          <router-link to="/profile/password" class="menu-item">
            <div class="menu-left">
              <span class="menu-icon">🔒</span>
              <span>비밀번호 변경</span>
            </div>
            <span class="menu-arrow">›</span>
          </router-link>

          <button @click="logout" class="menu-item logout-btn">
            <div class="menu-left">
              <span class="menu-icon">🚪</span>
              <span>로그아웃</span>
            </div>
            <span class="menu-arrow">›</span>
          </button>
        </div>
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
const user = ref({
  nickname: '',
  profile_image: '',
  bio: '',
  article_count: 0,
  follower_count: 0,
  following_count: 0,
})

// 프로필 데이터 가져오기 (인증 토큰 포함)
const fetchProfile = async () => {
  const token = localStorage.getItem('access_token') // 토큰 키 확인 필요
  try {
    const response = await axios.get('/mypage/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    user.value = response.data
  } catch (error) {
    console.error('프로필 로드 실패:', error)
    if (error.response?.status === 401) {
      router.push('/login')
    }
  }
}

const logout = () => {
  if (confirm('로그아웃 하시겠습니까?')) {
    localStorage.removeItem('access_token')
    delete axios.defaults.headers.common['Authorization']
    router.push('/login')
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.mypage {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%);
  padding: 40px 20px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

/* 프로필 헤더 */
.profile-header {
  margin-bottom: 40px;
}

.profile-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 50px;
  border-radius: 25px;
  color: white;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
  display: flex;
  gap: 40px;
  align-items: center;
}

.avatar-section {
  text-align: center;
}

.avatar {
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  margin-bottom: 15px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
}

.change-avatar-btn {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.change-avatar-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.profile-info {
  flex: 1;
}

.username {
  font-size: 2.5rem;
  font-weight: 900;
  margin-bottom: 8px;
}

.email {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 30px;
}

.stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 900;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

/* 섹션 */
.section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 20px;
}

/* 활동 카드 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.activity-card {
  background: white;
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.activity-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.activity-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.activity-card:hover::before {
  transform: scaleX(1);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.activity-card h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.activity-card p {
  color: #666;
  font-size: 0.95rem;
}

.card-arrow {
  position: absolute;
  top: 30px;
  right: 30px;
  font-size: 1.5rem;
  color: #667eea;
  opacity: 0;
  transition: all 0.3s;
}

.activity-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(5px);
}

/* 설정 메뉴 */
.menu-list {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.3s;
  cursor: pointer;
  background: none;
  border: none;
  border-bottom: 1px solid #f0f0f0;
  width: 100%;
  text-align: left;
  font-size: 1rem;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: #f8f9fa;
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.menu-icon {
  font-size: 1.5rem;
}

.menu-arrow {
  font-size: 1.5rem;
  color: #d0d0d0;
}

.logout-btn {
  color: #ff4444;
}

@media (max-width: 768px) {
  .profile-card {
    flex-direction: column;
    padding: 30px 20px;
    text-align: center;
  }

  .stats {
    justify-content: center;
  }

  .username {
    font-size: 2rem;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
