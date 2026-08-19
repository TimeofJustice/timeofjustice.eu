<script setup lang="ts">
import { Project } from "@/types/Project.ts";

import MissingTexture from "@assets/images/MissingTexture.svg";

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
  <div class="flex gap-2 overflow-hidden" v-motion-slide-visible-once-right>
    <v-lazy-image
      class="project-image h-auto max-w-full rounded-md object-cover"
      :src="project.title_image ? project.title_image.original : MissingTexture"
    />

    <div class="flex w-full items-center justify-between gap-1 overflow-hidden">
      <div class="flex flex-col gap-1 overflow-hidden">
        <div class="flex flex-row items-center gap-2">
          <UiBadge
            class="flex items-center"
            :class="`bg-${project.status.color}/50`"
            v-if="project.status"
          >
            {{ project.status.name }}
          </UiBadge>
          <h5 class="mb-0 truncate">{{ project.title }}</h5>
        </div>
        <div class="flex flex-wrap gap-1">
          <UiBadge
            v-for="technology in visibleTechnologies"
            :key="technology.name"
            class="bg-primary/50"
          >
            <iconify-icon :icon="technology.icon" v-if="technology.icon" />
            {{ technology.name }}
          </UiBadge>
          <UiBadge v-if="amountOfHiddenTechnologies > 0" class="bg-primary/50">
            +{{ amountOfHiddenTechnologies }}
          </UiBadge>
        </div>
      </div>

      <UiButton
        variant="tertiary"
        square
        class="after:absolute after:inset-0 after:z-1 after:content-['']"
        :to="'/projects/' + project.id"
        offcanvas-source="/"
      >
        <iconify-icon icon="fa6-solid:arrow-right" />
      </UiButton>
    </div>
  </div>
</template>

<style scoped>
.project-image {
  min-width: 7rem;
  max-width: 7rem;
  min-height: 7rem;
  max-height: 7rem;
}
</style>
