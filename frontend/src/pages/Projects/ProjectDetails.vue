<script setup lang="ts">
import { Project } from "@/types/Project.ts";
import { ref } from "vue";
import { TranslatedText } from "@/types/TranslatedText.ts";

interface Props {
  project: Project | null;
}

defineProps<Props>();

const imgSize = ref("250");
const imgButton = ref("fa-maximize");

const handleResize = () => {
  if (imgSize.value === "500") {
    imgSize.value = "250";
    imgButton.value = "fa-maximize";
  } else {
    imgSize.value = "500";
    imgButton.value = "fa-minimize";
  }
};
</script>

<template>
  <div class="d-flex flex-column gap-2" v-if="project">
    <h1 class="mb-0"> {{ project.title }} </h1>

    <div class="position-relative button-on-hover">
      <BCarousel
        :controls="1 < project.images.length"
        :indicators="1 < project.images.length"
        ride="carousel"
        :interval="500000"
        :img-height="imgSize"
        class="resizeable"
        v-if="0 < project.images.length">
        <BCarouselSlide :img-src="image.image.original" class="img-fluid object-fit-cover" v-for="(image, i) in project.images" :key="i"
                        :alt="image.alt[$i18n.locale as keyof TranslatedText]" />
      </BCarousel>

      <BButton variant="primary" class="position-absolute top-0 end-0 m-2 btn-square z-3" @click="handleResize">
        <font-awesome-icon :icon="['fa-solid', imgButton]" />
      </BButton>
    </div>

    <div class="d-flex gap-1 flex-wrap">
      <BBadge v-for="technology in project.technologies" :key="technology.name">
        <font-awesome-icon :icon="technology.icon" />
        {{ technology.name }}
      </BBadge>
    </div>

    <vue-markdown :source="project.description[$i18n.locale as keyof TranslatedText]" :options="{
      linkify: true
    }" />

    <div class="d-flex gap-2">
      <a :href="project.github" class="btn btn-primary d-flex gap-2 align-items-center" target="_blank" v-if="project.github">
        <font-awesome-icon icon="fa-brands fa-github" />
        Github
        <font-awesome-icon icon="fa-solid fa-external-link-alt" />
      </a>
      <a :href="project.website" class="btn btn-primary d-flex gap-2 align-items-center" target="_blank" v-if="project.website">
        <font-awesome-icon icon="fa-solid fa-globe" />
        Website
        <font-awesome-icon icon="fa-solid fa-external-link-alt" />
      </a>
    </div>
  </div>

  <div class="w-100 h-100 d-flex justify-content-center align-items-center" v-else>
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>