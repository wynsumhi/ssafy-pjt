// src/stores/savedVideos.js
import { ref, computed } from "vue";
import { defineStore } from "pinia";

export const useSavedVideosStore = defineStore("savedVideos", () => {
  // 상태: 저장된 비디오 목록
  const savedVideos = ref([]);

  // computed: 저장된 비디오 개수
  const savedCount = computed(() => savedVideos.value.length);

  // 초기화: localStorage에서 데이터 불러오기
  const initStore = () => {
    const stored = localStorage.getItem("savedVideos");
    if (stored) {
      savedVideos.value = JSON.parse(stored);
    }
  };

  // localStorage에 저장
  const saveToLocalStorage = () => {
    localStorage.setItem("savedVideos", JSON.stringify(savedVideos.value));
  };

  // 비디오 저장
  const saveVideo = (videoData) => {
    // 중복 체크
    const exists = savedVideos.value.some((video) => video.id === videoData.id);
    if (exists) {
      return false;
    }

    savedVideos.value.push(videoData);
    saveToLocalStorage();
    return true;
  };

  // 비디오 삭제
  const removeVideo = (videoId) => {
    savedVideos.value = savedVideos.value.filter(
      (video) => video.id !== videoId
    );
    saveToLocalStorage();
  };

  // 비디오가 저장되어 있는지 확인
  const isVideoSaved = (videoId) => {
    return savedVideos.value.some((video) => video.id === videoId);
  };

  // 모든 비디오 삭제
  const clearAll = () => {
    savedVideos.value = [];
    saveToLocalStorage();
  };

  return {
    savedVideos,
    savedCount,
    initStore,
    saveVideo,
    removeVideo,
    isVideoSaved,
    clearAll,
  };
});
