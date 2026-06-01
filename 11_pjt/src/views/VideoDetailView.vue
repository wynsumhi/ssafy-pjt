<template>
  <div class="video-detail-container">
    <GoBack />

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading">비디오 정보를 불러오는 중...</div>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- 비디오 상세 정보 -->
    <div v-if="videoDetail && !isLoading" class="video-content">
      <!-- 제목 -->
      <h1 class="video-title">{{ videoDetail.snippet.title }}</h1>

      <!-- 업로드 날짜 -->
      <p class="upload-date">
        업로드 날짜:
        {{
          new Date(videoDetail.snippet.publishedAt).toLocaleDateString("ko-KR")
        }}
      </p>

      <!-- YouTube iframe 플레이어 -->
      <div class="video-player">
        <iframe
          :src="`https://www.youtube.com/embed/${videoId}`"
          title="YouTube video player"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>

      <!-- 비디오 정보 섹션 -->
      <div class="video-info">
        <div class="channel-info">
          <h2 class="channel-title">{{ videoDetail.snippet.channelTitle }}</h2>
        </div>

        <!-- 설명 -->
        <div class="description-section">
          <h3>★ 영상 설명</h3>
          <p class="description">{{ videoDetail.snippet.description }}</p>
        </div>

        <!-- 저장 버튼 -->
        <button
          @click="toggleSaveVideo"
          :class="['save-button', { saved: isSaved }]"
        >
          {{ saveButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import GoBack from "@/components/GoBack.vue";
import { useSavedVideosStore } from "@/stores/savedVideos";

const route = useRoute();
const router = useRouter();
const savedVideosStore = useSavedVideosStore();

const videoId = route.params.videoId;
const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY;
const API_URL = "https://www.googleapis.com/youtube/v3/videos";

// 비디오 상세 정보
const videoDetail = ref(null);
const isLoading = ref(true);
const errorMessage = ref("");

// Pinia store에서 저장 여부 확인
const isSaved = computed(() => savedVideosStore.isVideoSaved(videoId));

// 버튼 텍스트
const saveButtonText = computed(() => {
  return isSaved.value ? "저장 취소" : "저장하기";
});

// 비디오 상세 정보 가져오기
const fetchVideoDetail = async () => {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await axios.get(API_URL, {
      params: {
        part: "snippet",
        id: videoId,
        key: API_KEY,
      },
    });

    // API 응답에서 첫 번째 항목 가져오기
    if (response.data.items && response.data.items.length > 0) {
      videoDetail.value = response.data.items[0];
    } else {
      errorMessage.value = "비디오 정보를 찾을 수 없습니다.";
    }
  } catch (error) {
    console.error("비디오 정보 로딩 오류:", error);
    errorMessage.value = "비디오 정보를 불러오는 중 오류가 발생했습니다.";
  } finally {
    isLoading.value = false;
  }
};

// 뒤로가기
const goBack = () => {
  router.back();
};

// 저장/취소 토글
const toggleSaveVideo = () => {
  if (isSaved.value) {
    // 저장 취소
    savedVideosStore.removeVideo(videoId);
    alert("저장이 취소되었습니다.");
  } else {
    // 저장하기
    const videoData = {
      id: videoId,
      title: videoDetail.value.snippet.title,
      channelTitle: videoDetail.value.snippet.channelTitle,
      thumbnail: videoDetail.value.snippet.thumbnails.medium.url,
    };

    const success = savedVideosStore.saveVideo(videoData);
    if (success) {
      alert("나중에 볼 동영상에 저장되었습니다!");
    } else {
      alert("이미 저장된 동영상입니다.");
    }
  }
};

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchVideoDetail();
});
</script>

<style scoped>
.video-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.back-button {
  padding: 8px 16px;
  margin-bottom: 20px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.back-button:hover {
  background-color: #e0e0e0;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.error-message {
  padding: 20px;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c00;
  text-align: center;
}

.video-content {
  background-color: white;
}

.video-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #030303;
}

.upload-date {
  font-size: 14px;
  color: #606060;
  margin-bottom: 16px;
}

/* YouTube iframe 반응형 컨테이너 */
.video-player {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 비율 */
  margin-bottom: 20px;
  background-color: #000;
}

.video-player iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-info {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.channel-info {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.channel-title {
  font-size: 18px;
  font-weight: 600;
  color: #030303;
  margin: 0;
}

.description-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #030303;
}

.description {
  font-size: 14px;
  line-height: 1.6;
  color: #030303;
  white-space: pre-wrap; /* 줄바꿈 유지 */
  word-wrap: break-word;
  margin-bottom: 20px;
}

.save-button {
  width: 100%;
  padding: 12px;
  background-color: #065fd4;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-button:hover {
  background-color: #0550b8;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .video-detail-container {
    padding: 10px;
  }

  .video-title {
    font-size: 18px;
  }

  .video-info {
    padding: 16px;
  }
}
</style>
