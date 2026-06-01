<template>
  <NavBar />
  <div class="container mt-4">
    <RouterView />
  </div>
</template>
<script setup>
import { onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { useSavedVideosStore } from "@/stores/savedVideos";
import NavBar from "@/components/Navbar.vue";

const savedVideosStore = useSavedVideosStore();

// 앱 시작 시 localStorage에서 데이터 불러오기
onMounted(() => {
  savedVideosStore.initStore();
});
</script>
<style scoped></style>
