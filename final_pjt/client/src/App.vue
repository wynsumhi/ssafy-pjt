<template>
  <div id="app">
    <HeaderNav />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <FooterNav />
  </div>
</template>

<script setup>
import FooterNav from '@/components/common/FooterNav.vue'
import HeaderNav from '@/components/common/HeaderNav.vue'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.checkAuth()
})
</script>

<style lang="scss">
@use '@/assets/styles/global.scss';

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  width: 100%;
}

// 페이지 전환 애니메이션
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
