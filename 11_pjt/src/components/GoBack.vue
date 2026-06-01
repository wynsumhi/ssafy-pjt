<template>
  <div>
    <button @click="goBack" class="btn btn-secondary mb-3">← 뒤로가기</button>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
const router = useRouter();
function goBack() {
  router.back();
}
</script>

<style lang="scss" scoped></style>
