<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="logo-big">🌍</div>
        <h1 class="title">지구깡</h1>
        <h2 class="subtitle">지역 구석구석을 깡(언박싱)하세요!</h2>
        <p class="description">
          당신의 주변에 숨겨진 보물 같은 장소들을 랜덤으로 발견하세요.
          <br />
          새로운 모험이 기다리고 있습니다! 🎯
        </p>
        <div class="button-group">
          <router-link v-if="isAuthenticated" to="/random" class="main-button">
            지금 시작하기
          </router-link>
          <template v-else>
            <router-link to="/signup" class="main-button">회원가입</router-link>
            <router-link to="/login" class="sub-button">로그인</router-link>
          </template>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="feature-card" v-for="feature in features" :key="feature.icon">
        <div class="feature-icon">{{ feature.icon }}</div>
        <h3 class="feature-title">{{ feature.title }}</h3>
        <p class="feature-description">{{ feature.description }}</p>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">지금 바로 시작하세요!</h2>
        <p class="cta-description">무료로 가입하고 당신만의 특별한 장소를 발견해보세요</p>
        <router-link to="/signup" class="cta-button">무료 회원가입</router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)

const features = [
  {
    icon: '🎲',
    title: '랜덤 추천',
    description: '운명에 맡기고 새로운 장소를 발견해보세요.',
  },
  {
    icon: '🗺️',
    title: '위치 기반',
    description: '내 주변의 숨은 맛집, 카페, 스팟을 지도에서 확인하세요.',
  },
  {
    icon: '🎯',
    title: '카테고리 필터',
    description: '원하는 카테고리로 필터링해서 찾아보세요.',
  },
  {
    icon: '🤖',
    title: 'AI 추천',
    description: '당신의 취향을 학습해서 개인화된 장소를 추천합니다.',
  },
  {
    icon: '💬',
    title: '후기 공유',
    description: '다녀온 장소의 후기를 작성하고 경험을 공유하세요.',
  },
  {
    icon: '👥',
    title: '소셜 기능',
    description: '비슷한 취향의 사람들을 팔로우하고 추천을 받아보세요.',
  },
]
</script>

<style scoped lang="scss">
.home {
  width: 100%;
}

.hero {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
}

.hero-content {
  text-align: center;
  max-width: 800px;
}

.logo-big {
  font-size: 6rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.title {
  font-size: 4rem;
  font-weight: 800;
  margin-bottom: 1rem;

  @media (max-width: 768px) {
    font-size: 3rem;
  }
}

.subtitle {
  font-size: 1.8rem;
  font-weight: 400;
  margin-bottom: 1.5rem;
  opacity: 0.9;
}

.description {
  font-size: 1.2rem;
  line-height: 1.8;
  margin-bottom: 3rem;
  opacity: 0.9;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.main-button {
  padding: 1.2rem 3rem;
  background: white;
  color: #667eea;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  }
}

.sub-button {
  padding: 1.2rem 3rem;
  background: transparent;
  color: white;
  border: 2px solid white;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  transition: all 0.3s;

  &:hover {
    background: white;
    color: #667eea;
    transform: translateY(-5px);
  }
}

.features {
  max-width: 1200px;
  margin: 0 auto;
  padding: 6rem 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  }
}

.feature-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.feature-title {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.feature-description {
  color: #666;
  line-height: 1.6;
}

.cta-section {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 6rem 2rem;
  text-align: center;
}

.cta-content {
  max-width: 800px;
  margin: 0 auto;
}

.cta-title {
  font-size: 3rem;
  color: white;
  margin-bottom: 1rem;
}

.cta-description {
  font-size: 1.3rem;
  color: white;
  opacity: 0.9;
  margin-bottom: 2.5rem;
}

.cta-button {
  display: inline-block;
  padding: 1.2rem 3rem;
  background: white;
  color: #f5576c;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  }
}
</style>
