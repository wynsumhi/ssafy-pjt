<script setup>
import { useRouter } from "vue-router";
import { useSavedVideosStore } from "@/stores/savedVideos";
import GoBack from "@/components/GoBack.vue";

const router = useRouter();
const savedVideosStore = useSavedVideosStore();

const deleteVideo = (videoId) => {
  if (confirm("이 영상을 삭제하시겠습니까?")) {
    savedVideosStore.removeVideo(videoId);
  }
};

const goToDetail = (videoId) => {
  router.push({
    name: "VideoDetail",
    params: { videoId },
  });
};
</script>

<template>
  <div class="later-container">
    <GoBack />
    <h1>나중에 볼 동영상</h1>

    <div v-if="savedVideosStore.savedCount === 0" class="empty-state">
      <p>등록된 비디오 없음</p>
    </div>

    <div v-else class="saved-grid">
      <div
        v-for="video in savedVideosStore.savedVideos"
        :key="video.id"
        class="saved-item"
      >
        <div class="video-card" @click="goToDetail(video.id)">
          <img :src="video.thumbnail" :alt="video.title" class="thumbnail" />
          <div class="video-info">
            <h3 class="video-title">{{ video.title }}</h3>
            <p class="channel-name">{{ video.channelTitle }}</p>
          </div>
        </div>

        <button @click.stop="deleteVideo(video.id)" class="delete-button">
          삭제
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.later-container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 28px;
  margin-bottom: 30px;
  color: #030303;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #606060;
}

.empty-state p {
  font-size: 18px;
  margin: 0;
}

.saved-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.saved-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
  transition: box-shadow 0.2s;
}

.saved-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.video-card {
  cursor: pointer;
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

.delete-button {
  width: 100%;
  padding: 10px;
  background-color: #f0f0f0;
  border: none;
  border-top: 1px solid #e0e0e0;
  cursor: pointer;
  font-size: 14px;
  color: #606060;
  transition: background-color 0.2s;
}

.delete-button:hover {
  background-color: #ffebee;
  color: #c62828;
}

@media (max-width: 768px) {
  .saved-grid {
    grid-template-columns: 1fr;
  }
}
</style>
