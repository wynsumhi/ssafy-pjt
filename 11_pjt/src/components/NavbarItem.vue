<!-- components/NavbarItem.vue -->
<template>
  <li class="nav-item">
    <RouterLink
      class="nav-link"
      :to="to"
      active-class="active"
      :aria-current="isActive ? 'page' : undefined"
    >
      {{ label }}
    </RouterLink>
  </li>
</template>

<script setup>
import { RouterLink, useRoute } from "vue-router";
import { computed } from "vue";

const props = defineProps({
  to: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
});

const route = useRoute();
const isActive = computed(() => route.path === props.to);
</script>
