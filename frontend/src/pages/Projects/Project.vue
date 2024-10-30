<script setup lang="ts">
import { Project } from "@types/Project.vue";

interface Props {
  project: Project;
  callback: (id: number) => void;
}

defineProps<Props>();
</script>

<template>
  <div class="d-flex gap-2" v-motion-slide-visible-once-right>
    <img class="img-fluid rounded" :src="project.title_image" style="width: 7rem; height: 7rem; object-fit: cover;">

    <div class="d-flex w-100 justify-content-between">
      <div class="align-content-center">
        <h5 class="text-white mb-0">{{ project.title }}</h5>
        <p class="text-grey-100 fw-bold mb-0">{{ project.short_description[$i18n.locale] }}</p>
      </div>

      <div class="align-content-center text-white">
        <a class="stretched-link stretched-link-translate-right" @click="callback(project.id)">
          <font-awesome-icon icon="fa-solid fa-arrow-right" />
        </a>
      </div>
    </div>
  </div>
</template>