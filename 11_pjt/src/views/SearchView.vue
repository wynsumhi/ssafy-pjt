<template>
  <GoBack />
  <div class="search-container container">
    <h1>비디오 검색</h1>
    <div class="input-group mb-3 search-box">
      <input
        v-model="searchKeyword"
        @keypress="handleKeyPress"
        type="text"
        class="form-control search-input"
        placeholder="관심 종목을 입력하세요"
        aria-label="interesting stock name"
        aria-describedby="button-addon2"
      />
      <button
        @click="performSearch"
        class="btn btn-outline-secondary search-button"
        type="button"
        id="button-addon2"
      >
        찾기
      </button>
    </div>

    <!-- 에러 메시지 -->
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <!-- 로딩 표시 -->
    <p v-if="isLoading" class="loading">검색 중...</p>

    <!-- 검색 결과 그리드 -->
    <div
      v-if="searchResults.length > 0"
      class="results-grid row row-cols-1 row-cols-md-2 row-cols-lg-3 mt-4"
    >
      <VideoCard
        v-for="video in searchResults"
        :key="video.id.videoId"
        :video="video"
      />
    </div>

    <!-- 결과 없음 메시지 -->
    <p
      v-if="!isLoading && searchResults.length === 0 && searchKeyword"
      class="no-results"
    >
      검색 결과가 없습니다.
    </p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import GoBack from "@/components/GoBack.vue";
import VideoCard from "@/components/VideoCard.vue";

const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY;
const API_URL = "https://www.googleapis.com/youtube/v3/search";

const searchKeyword = ref("");
const searchResults = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");

// 검색 실행 함수
const performSearch = async () => {
  // 검색어가 비어있으면 실행하지 않음
  if (!searchKeyword.value.trim()) {
    errorMessage.value = "검색어를 입력해주세요.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await axios.get(API_URL, {
      params: {
        part: "snippet",
        q: searchKeyword.value,
        key: API_KEY,
        maxResults: 10,
        type: "video",
      },
    });

    // 검색 결과 저장
    searchResults.value = response.data.items;
  } catch (error) {
    console.error("검색 오류:", error);
    errorMessage.value = "검색 중 오류가 발생했습니다.";
  } finally {
    isLoading.value = false;
  }
};

// Enter 키 이벤트 핸들러
const handleKeyPress = (event) => {
  if (event.key === "Enter") {
    performSearch();
  }
};
</script>

<style scoped>
.search-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.search-button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #ff0000;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-button:hover {
  background-color: #cc0000;
}
.error-message {
  color: red;
  margin-bottom: 10px;
}

.loading {
  text-align: center;
  color: #666;
}
</style>
