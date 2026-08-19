<script setup lang="ts">
import { Project } from "@/types/Project.ts";
import { Head } from "@inertiajs/vue3";

import ProjectCarousel from "@components/ProjectCarousel.vue";

interface ProjectPageProps {
  project: Project;
}

defineProps<ProjectPageProps>();
</script>

<template>
  <Head :title="project.title" />

  <div class="container-page">
    <div class="flex flex-col gap-2">
      <div class="flex items-center justify-between gap-2">
        <h1 class="mb-0 truncate">{{ project.title }}</h1>
        <UiBadge
          class="flex items-center"
          :class="`bg-${project.status.color}/50`"
          v-if="project.status"
        >
          {{ project.status.name }}
        </UiBadge>
      </div>

      <div class="flex flex-wrap gap-1">
        <UiBadge
          v-for="technology in project.technologies"
          :key="technology.name"
          variant="primary"
        >
          <iconify-icon :icon="technology.icon" v-if="technology.icon" />
          {{ technology.name }}
        </UiBadge>
      </div>

      <ProjectCarousel :items="project.images" />

      <div class="flex flex-col-reverse justify-between gap-2 lg:flex-row">
        <vue-markdown
          class="markdown-body"
          :source="project.description || $t('general.no_description')"
          :options="{
            linkify: true,
          }"
        />

        <div class="flex flex-col items-stretch gap-2 lg:w-1/5 lg:shrink-0">
          <UiButton
            variant="primary"
            :to="project.github"
            external
            target="_blank"
            v-if="project.github"
          >
            <iconify-icon icon="fa6-brands:github" />
            Github
            <iconify-icon icon="pajamas:external-link" />
          </UiButton>
          <UiButton
            variant="primary"
            :to="project.website"
            external
            target="_blank"
            v-if="project.website"
          >
            <iconify-icon icon="fa6-solid:globe" />
            Website
            <iconify-icon icon="pajamas:external-link" />
          </UiButton>
        </div>
      </div>
    </div>
  </div>
</template>
