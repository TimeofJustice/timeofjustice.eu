<script setup lang="ts">
import { Project } from "@/types/Project.ts";
import { TranslatedText } from "@/types/TranslatedText.ts";

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
    <v-lazy-image
      class="img-fluid object-fit-cover rounded"
      style="
        min-width: 7rem;
        max-width: 7rem;
        min-height: 7rem;
        max-height: 7rem;
      "
      :src="
        project.title_image
          ? project.title_image.original
          : require('@assets/images/MissingTexture.svg')
      "
      :src-placeholder="project.title_image ? project.title_image.lazy : ''"
    />

    <div class="d-flex w-100 justify-content-between overflow-hidden gap-1">
      <div
        class="align-content-center d-flex flex-column justify-content-center overflow-hidden"
      >
        <div class="d-flex flex-row gap-2 align-items-center">
          <BBadge
            class="d-flex align-items-center bg-opacity-50"
            :variant="project.status.color"
            v-if="project.status"
            >{{
              project.status.name[$i18n.locale as keyof TranslatedText]
            }}</BBadge
          >
          <h5 class="mb-0 text-truncate">{{ project.title }}</h5>
        </div>
        <p class="text-accent fw-semibold mb-0 text-truncate">
          {{ project.short_description[$i18n.locale as keyof TranslatedText] }}
        </p>
        <div class="d-flex gap-1 flex-wrap">
          <BBadge
            v-for="technology in technologies"
            :key="technology.name"
            class="bg-opacity-50"
            variant="primary"
          >
            <iconify-icon :icon="technology.icon" v-if="technology.icon" />
            {{ technology.name }}
          </BBadge>
          <BBadge v-if="leftover > 0" class="bg-opacity-50" variant="primary">
            +{{ leftover }}
          </BBadge>
        </div>
      </div>

      <div class="align-content-center">
        <BButton
          variant="tertiary"
          class="btn-square stretched-link"
          @click="callback(project.id)"
        >
          <iconify-icon icon="fa6-solid:arrow-right" />
        </BButton>
      </div>
    </div>
  </div>
</template>
