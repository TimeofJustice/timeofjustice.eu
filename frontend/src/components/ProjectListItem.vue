<script setup lang="ts">
import { Project } from "@/types/Project.ts";
import { TranslatedText } from "@/types/TranslatedText.ts";

import MissingTexture from '@assets/images/MissingTexture.svg'

interface ProjectListItemProps {
  project: Project;
  amountOfTechnologies?: number;
}

const { project, amountOfTechnologies = 5 } =
  defineProps<ProjectListItemProps>();

const visibleTechnologies = project.technologies.slice(0, amountOfTechnologies);
const amountOfHiddenTechnologies =
  project.technologies.length - visibleTechnologies.length;
</script>

<template>
  <div class="d-flex gap-2 overflow-hidden" v-motion-slide-visible-once-right>
    <v-lazy-image
      class="project-image img-fluid object-fit-cover rounded"
      :src="project.title_image ? project.title_image.original : MissingTexture"
    />

    <div
      class="d-flex w-100 justify-content-between align-items-center overflow-hidden gap-1"
    >
      <div class="d-flex flex-column overflow-hidden gap-1">
        <div class="d-flex flex-row gap-2 align-items-center">
          <BBadge
            class="d-flex align-items-center bg-opacity-50"
            :variant="project.status.color"
            v-if="project.status"
          >
            {{ project.status.name[$i18n.locale as keyof TranslatedText] }}
          </BBadge>
          <h5 class="mb-0 text-truncate">{{ project.title }}</h5>
        </div>
        <div class="d-flex gap-1 flex-wrap">
          <BBadge
            v-for="technology in visibleTechnologies"
            :key="technology.name"
            class="bg-opacity-50"
            variant="primary"
          >
            <iconify-icon :icon="technology.icon" v-if="technology.icon" />
            {{ technology.name }}
          </BBadge>
          <BBadge
            v-if="amountOfHiddenTechnologies > 0"
            class="bg-opacity-50"
            variant="primary"
          >
            +{{ amountOfHiddenTechnologies }}
          </BBadge>
        </div>
      </div>

      <BButton
        variant="tertiary"
        class="btn-square stretched-link"
        :to="'/projects/' + project.id"
        offcanvas-source="/"
      >
        <iconify-icon icon="fa6-solid:arrow-right" />
      </BButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
.project-image {
  min-width: 7rem;
  max-width: 7rem;
  min-height: 7rem;
  max-height: 7rem;
}
</style>
