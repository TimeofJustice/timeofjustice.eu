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
    <v-lazy-image class="img-fluid rounded" style="width: 7rem; height: 7rem; object-fit: cover;"
                  :src="project.title_image ? project.title_image.original : require('@assets/images/MissingTexture.svg')"
                  :src-placeholder="project.title_image ? project.title_image.lazy : ''" />

    <div class="d-flex w-100 justify-content-between overflow-hidden gap-1">
      <div class="align-content-center d-flex flex-column justify-content-center overflow-hidden">
        <div class="d-flex flex-row gap-2 align-items-center">
          <BBadge class="d-flex align-items-center" :class="project.status.color ? 'bg-' + project.status.color : ''"
                  v-if="project.status">{{ project.status.name[$i18n.locale] }}</BBadge>
          <h5 class="text-white mb-0 text-truncate">{{ project.title }}</h5>
        </div>
        <p class="text-grey-100 fw-bold mb-0 text-truncate">{{ project.short_description[$i18n.locale] }}</p>
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
        <a class="stretched-link stretched-link-translate-right" href="#" @click="callback(project.id)">
          <font-awesome-icon icon="fa-solid fa-arrow-right" />
        </a>
      </div>
    </div>
  </div>
</template>