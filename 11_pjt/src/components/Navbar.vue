<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
      <RouterLink class="navbar-brand" to="/">MyTube</RouterLink>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <NavbarItem to="/" label="Home" />
          <NavbarItem to="/search" label="Search" />
          <NavbarItem
            to="/later"
            :label="`Later ${savedCount > 0 ? `(${savedCount})` : ''}`"
          />
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";
import NavbarItem from "@/components/NavbarItem.vue";
import { useSavedVideosStore } from "@/stores/savedVideos";

const savedVideosStore = useSavedVideosStore();
const savedCount = computed(() => savedVideosStore.savedCount);
</script>
