<script setup lang="ts">
import { Project } from "@/types/Project.ts";
import { Head } from "@inertiajs/vue3";
import { TranslatedText } from "@/types/TranslatedText.ts";

import ProjectCarousel from "@components/ProjectCarousel.vue";

interface ProjectPageProps {
  project: Project;
}

defineProps<ProjectPageProps>();
</script>

<template>
  <Head :title="project.title" />

  <div class="container-xxl">
    <div class="d-flex flex-column gap-2">
      <div class="d-flex gap-2 align-items-center justify-content-between">
        <h1 class="mb-0 text-truncate">{{ project.title }}</h1>
        <BBadge
          class="d-flex align-items-center bg-opacity-50"
          :variant="project.status.color"
          v-if="project.status"
        >
          {{ project.status.name[$i18n.locale as keyof TranslatedText] }}
        </BBadge>
      </div>

      <div class="d-flex gap-1 flex-wrap">
        <BBadge
          v-for="technology in project.technologies"
          :key="technology.name"
          variant="primary"
        >
          <iconify-icon :icon="technology.icon" v-if="technology.icon" />
          {{ technology.name }}
        </BBadge>
      </div>

      <ProjectCarousel :items="project.images" />

      <div
        class="d-flex gap-2 justify-content-between flex-column-reverse flex-lg-row"
      >
        <vue-markdown
          class="markdown-body"
          :source="
            project.description[$i18n.locale as keyof TranslatedText] ||
            $t('general.no_description')
          "
          :options="{
            linkify: true,
          }"
        />

        <div class="d-flex flex-column gap-2 align-items-stretch col-lg-2">
          <BButton
            variant="primary"
            :to="project.github"
            external
            target="_blank"
            v-if="project.github"
          >
            <iconify-icon icon="fa6-brands:github" />
            Github
            <iconify-icon icon="pajamas:external-link" />
          </BButton>
          <BButton
            variant="primary"
            :to="project.website"
            external
            target="_blank"
            v-if="project.website"
          >
            <iconify-icon icon="fa6-solid:globe" />
            Website
            <iconify-icon icon="pajamas:external-link" />
          </BButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
