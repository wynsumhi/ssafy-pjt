<template>
  <header class="header">
    <div class="header-container">
      <router-link to="/" class="logo"> 🌍 지구깡 </router-link>

      <nav class="nav nav-links">
        <template v-if="isLoggedIn">
          <router-link to="/random" class="nav-link">랜덤 뽑기</router-link>
          <router-link to="/articles/list" class="nav-link">피드</router-link>
          <router-link :to="`/profile/${user?.username}`" class="nav-link">
            <div class="user-info">
              <span class="nickname">{{ user?.nickname }}님</span>
              <button @click="handleLogout" class="logout-btn">로그아웃</button>
            </div>
          </router-link>
        </template>

        <template v-else>
          <router-link to="/login" class="nav-link">로그인</router-link>
          <router-link to="/signup" class="signup-btn">회원가입</router-link>
        </template>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const { user, isLoggedIn } = storeToRefs(authStore)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>

<style scoped lang="scss">
.header {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ff6b6b;
  transition: color 0.2s;

  &:hover {
    color: #ff5252;
  }
}

.nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: #333;
  font-weight: 500;
  transition: color 0.2s;

  &:hover {
    color: #ff6b6b;
  }

  &.router-link-active {
    color: #ff6b6b;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;

  .nickname {
    color: #666;
  }
}

.logout-btn {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  transition: background 0.2s;

  &:hover {
    background: #e0e0e0;
  }
}

.signup-btn {
  padding: 0.5rem 1rem;
  background: #ff6b6b;
  color: white;
  border-radius: 4px;
  transition: background 0.2s;

  &:hover {
    background: #ff5252;
  }
}

@media (max-width: 768px) {
  .header-container {
    padding: 1rem;
  }

  .nav {
    gap: 1rem;
    font-size: 0.9rem;
  }

  .user-info {
    gap: 0.5rem;
  }
}
</style>
