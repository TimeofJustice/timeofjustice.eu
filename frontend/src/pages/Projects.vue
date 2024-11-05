<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { ref } from "vue";
import Profile from "@pages/Projects/Profile.vue";
import ProjectDetails from "@pages/Projects/ProjectDetails.vue";
import { Social } from "@/types/Social.vue";
import { Project } from "@/types/Project.vue";
import ProjectItem from "@pages/Projects/ProjectItem.vue";

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
</script>

<template>
  <Head title="Projects" />

  <div class="d-flex container gap-4 flex-column flex-lg-row">
    <div class="col-md-4 flex-grow-0 justify-content-start align-items-end d-none d-lg-flex flex-column">
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

    <div class="d-flex flex-column h-100 flex-grow-1 flex-shrink-1 gap-2" style="min-width: 0">
      <section v-motion-slide-visible-once-top v-if="true">
        <h1 class="display-1 fw-bold text-white" style="line-height: 50px">
          Past
          <br>
          <span class="display-1 fw-bold text-grey-100">Projects</span>
        </h1>
        <div class="d-flex flex-column gap-3">
          <ProjectItem :project="project" v-for="(project, i) in projects" :callback="loadProject" :key="i" />
        </div>
      </section>
    </div>
  </div>

  <BOffcanvas v-model="showOffcanvas" placement="end">
    <template #header>
      <div class="d-flex gap-2">
        <a type="button" class="btn btn-primary" @click="showOffcanvas = false">
          <font-awesome-icon icon="fa-solid fa-times" />
        </a>
        <a type="button" class="btn btn-primary" :href="`/project/${project?.id}`">
          <font-awesome-icon icon="fa-solid fa-external-link-alt" />
        </a>
      </div>
    </template>

    <slot name="offcanvas-body">
      <ProjectDetails :project="project"/>
    </slot>
  </BOffcanvas>
</template>