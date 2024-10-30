<script setup lang="ts">
import { Project } from "@types/Project.vue";

interface Props {
  project: Project;
  callback: (id: number) => void;
}

const props = defineProps<Props>();

const visibleTechnologies = 5;
const technologies = props.project.technologies.slice(0, visibleTechnologies);
const leftover = props.project.technologies.length - technologies.length;
</script>

<template>
  <div class="d-flex gap-2 overflow-hidden" v-motion-slide-visible-once-right>
    <img class="img-fluid rounded" :src="project.title_image" style="width: 7rem; height: 7rem; object-fit: cover;">

    <div class="d-flex w-100 justify-content-between overflow-hidden gap-1">
      <div class="align-content-center d-flex flex-column justify-content-center overflow-hidden">
        <h5 class="text-white mb-0">{{ project.title }}</h5>
        <p class="text-grey-100 fw-bold mb-0 text-truncate">{{ project.short_description[$i18n.locale] }} {{ project.short_description[$i18n.locale] }}</p>
        <div class="d-flex gap-1 flex-wrap">
          <BBadge v-for="technology in technologies" :key="technology">
            <font-awesome-icon :icon="technology.icon" />
            {{ technology.name }}
          </BBadge>
          <BBadge v-if="leftover > 0">
            +{{ leftover }}
          </BBadge>
        </div>
      </div>

      <div class="align-content-center text-white">
        <a class="stretched-link stretched-link-translate-right" @click="callback(project.id)">
          <font-awesome-icon icon="fa-solid fa-arrow-right" />
        </a>
      </div>
    </div>
  </div>
</template>