<script setup lang="ts">
import { Project } from "@/types/Project.ts";
import { TranslatedText } from "@/types/TranslatedText.ts";
import Carousel from "@components/Carousel.vue";

interface Props {
  project: Project | null;
}

defineProps<Props>();
</script>

<template>
  <div class="d-flex flex-column gap-2" v-if="project">
    <div class="d-flex gap-2 align-items-center justify-content-between">
      <h1 class="mb-0 text-truncate">{{ project.title }}</h1>
      <BBadge
        class="d-flex align-items-center bg-opacity-50"
        :variant="project.status.color"
        v-if="project.status"
        >{{ project.status.name[$i18n.locale as keyof TranslatedText] }}</BBadge
      >
    </div>

    <Carousel :items="project.images" />

    <div class="d-flex gap-1 flex-wrap">
      <BBadge
        v-for="technology in project.technologies"
        :key="technology.name"
        class="bg-opacity-50"
      >
        <font-awesome-icon :icon="technology.icon" v-if="technology.icon" />
        {{ technology.name }}
      </BBadge>
    </div>

    <vue-markdown
      :source="project.description[$i18n.locale as keyof TranslatedText]"
      :options="{
        linkify: true,
      }"
    />

    <div class="d-flex gap-2">
      <BLink
        :to="project.github"
        external
        class="btn btn-primary d-flex gap-2 align-items-center"
        target="_blank"
        v-if="project.github"
      >
        <font-awesome-icon icon="fa-brands fa-github" />
        Github
        <font-awesome-icon icon="fa-solid fa-external-link-alt" />
      </BLink>
      <BLink
        :to="project.website"
        external
        class="btn btn-primary d-flex gap-2 align-items-center"
        target="_blank"
        v-if="project.website"
      >
        <font-awesome-icon icon="fa-solid fa-globe" />
        Website
        <font-awesome-icon icon="fa-solid fa-external-link-alt" />
      </BLink>
    </div>
  </div>

  <div
    class="w-100 h-100 d-flex justify-content-center align-items-center"
    v-else
  >
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>
