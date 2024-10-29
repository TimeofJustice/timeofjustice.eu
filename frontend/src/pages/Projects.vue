<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { ref } from "vue";
import Profile from "@components/Profile.vue";
import { Social } from "@types/Social.vue";
import { TranslatedText } from "../types/TranslatedText.vue";

interface Project {
  id: number;
  title: string;
  short_description: TranslatedText,
  description: TranslatedText,
  title_image: string,
  images: string[],
  technologies: string[],
  github: string,
  website: string,
}

interface Props {
  socials: Social[];
  projects: Project[];
}

defineProps<Props>();

const project = ref<Project | null>(null);

const showOffcanvas = ref(false);

const loadProject = async (id: number) => {
  project.value = null;
  showOffcanvas.value = true;

  const response = await fetch(`/api/project/${id}`);
  if (!response.ok) {
    throw new Error("Failed to load project");
  }

  project.value = await response.json();
};

const imgSize = ref(250);
const imgButton = ref("fa-maximize");

const handleResize = () => {
  if (imgSize.value === 500) {
    imgSize.value = 250;
    imgButton.value = "fa-maximize";
  } else {
    imgSize.value = 500;
    imgButton.value = "fa-minimize";
  }
};
</script>

<template>
  <Head title="Projects" />

  <div class="d-flex container gap-4 flex-column flex-lg-row">
    <div class="col-md-4 flex-grow-1 justify-content-start align-items-end d-none d-lg-flex flex-column">
      <!-- If you found this, keep this our dirty little secret -->
      <h1 class="display-1 fw-bold text-white invisible" style="line-height: 50px;">
        Past
        <br>
        <span class="display-1 fw-bold text-grey-100">Projects</span>
      </h1>
      <Profile :socials="socials" class="position-sticky" style="top: 1rem;" />
    </div>
    <div class="d-flex flex-grow-1 justify-content-end align-items-start d-block d-lg-none">
      <Profile :socials="socials" variant="small" />
    </div>

    <div class="d-flex flex-column h-100 w-100 gap-2">
      <section v-motion-slide-visible-once-top v-if="true">
        <h1 class="display-1 fw-bold text-white" style="line-height: 50px">
          Past
          <br>
          <span class="display-1 fw-bold text-grey-100">Projects</span>
        </h1>
        <div class="d-flex flex-column gap-3">
          <div class="d-flex gap-2" v-motion-slide-visible-once-right v-for="(project, i) in projects" :key="project.id">
            <img class="img-fluid rounded" :src="project.title_image" style="width: 7rem; height: 7rem; object-fit: cover;">

            <div class="d-flex w-100 justify-content-between">
              <div class="align-content-center">
                <h5 class="text-white mb-0">{{ project.title }}</h5>
                <p class="text-grey-100 fw-bold mb-0">{{ project.short_description[$i18n.locale] }}</p>
              </div>

              <div class="align-content-center text-white">
                <a class="stretched-link stretched-link-translate-right" @click="loadProject(i)">
                  <font-awesome-icon icon="fa-solid fa-arrow-right" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>

  <BOffcanvas v-model="showOffcanvas" placement="end">
    <template #header>
      <h5 class="mb-0">{{ project?.title }} ({{ project?.id }})</h5>
      <button type="button" class="btn-close" @click="showOffcanvas = false">
        <font-awesome-icon icon="fa-solid fa-times" />
      </button>
    </template>

    <slot name="offcanvas-body">
      <div class="position-relative button-on-hover" v-if="project">
        <BCarousel controls indicators ride="carousel" interval="2500" :img-height="imgSize" class="resizeable">
          <BCarouselSlide img-src="https://picsum.photos/1024/480/?image=1" class="img-fluid" />
          <BCarouselSlide img-src="https://picsum.photos/1024/480/?image=2" class="img-fluid" />
          <BCarouselSlide img-src="https://picsum.photos/1024/480/?image=3" class="img-fluid" />
          <BCarouselSlide :img-src="require('@assets/images/TimeofJustice.jpg')" class="img-fluid" />
        </BCarousel>

        <div class="position-absolute top-0 end-0 m-2 btn btn-primary z-3" @click="handleResize">
          <font-awesome-icon :icon="['fa-solid', imgButton]" />
        </div>
      </div>

      <div class="w-100 h-100 d-flex justify-content-center align-items-center" v-else>
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </slot>
  </BOffcanvas>
</template>

<style scoped lang="scss">

</style>