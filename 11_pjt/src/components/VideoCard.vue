<template>
  <div class="g-2">
    <div class="video-card card p-0 h-100" @click="goToDetail">
      <!-- 썸네일 -->
      <img
        :src="video.snippet.thumbnails.medium.url"
        :alt="video.snippet.title"
        class="thumbnail"
      />

      <!-- 비디오 정보 -->
      <div class="video-info card-body">
        <h3 class="video-title card-title">{{ video.snippet.title }}</h3>
        <p class="channel-name card-text">{{ video.snippet.channelTitle }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

// props 정의 - 부모로부터 비디오 데이터를 받음
const props = defineProps({
  video: {
    type: Object,
    required: true,
  },
});

const router = useRouter();

// 카드 클릭 시 상세 페이지로 이동
const goToDetail = () => {
  router.push({
    name: "VideoDetail",
    params: { videoId: props.video.id.videoId },
  });
};
</script>

<style>
.video-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.video-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.thumbnail {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.video-info {
  padding: 12px;
}

.video-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #030303;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.channel-name {
  margin: 0;
  color: #606060;
  font-size: 14px;
}
</style>
