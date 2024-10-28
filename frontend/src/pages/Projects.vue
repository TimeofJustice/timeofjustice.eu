<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { ref } from "vue";
import Profile from "@components/Profile.vue";
import { Social } from "@types/Social.vue";

interface Project {
  id: number;
  title: string;
}

interface Props {
  socials: Social[];
}

defineProps<Props>();

const project = ref<Project | null>(null);

const showOffcanvas = ref(false);

const loadProject = async (id: number) => {
  const response = await fetch(`/api/project/${id}`);

  if (!response.ok) {
    throw new Error("Failed to load project");
  }

  showOffcanvas.value = true;
  project.value = await response.json();
};
</script>

<template>
  <Head title="Projects"/>

  <div class="d-flex container gap-4 flex-column flex-lg-row">
    <div class="col-md-4 flex-grow-1 justify-content-end align-items-start d-none d-lg-flex" style="padding-top: 10rem">
      <Profile :socials="socials" class="position-sticky" style="top: 1rem;"/>
    </div>
    <div class="d-flex flex-grow-1 justify-content-end align-items-start d-block d-lg-none">
      <Profile :socials="socials" variant="small"/>
    </div>

    <div class="d-flex flex-column h-100 w-100 gap-2">
      <section v-motion-slide-visible-once-top v-if="true">
        <h1 class="display-1 fw-bold text-white" style="line-height: 50px">
          Past
          <br>
          <span class="display-1 fw-bold text-grey-100">Projects</span>
        </h1>
        <div class="d-flex flex-column gap-3">
          <div class="d-flex gap-2" v-motion-slide-visible-once-right v-for:let="i in 40" :key="i">
            <img class="img-fluid rounded" :src="require('@assets/images/TimeofJustice.jpg')" style="width: 7rem">

            <div class="d-flex w-100 justify-content-between">
              <div class="align-content-center">
                <h5 class="text-white mb-0">Project title</h5>
                <p class="text-grey-100 fw-bold">Project description</p>
              </div>

              <div class="align-content-center text-white">
                <a class="stretched-link stretched-link-translate-right" @click="loadProject(1)">
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
      <slot name="offcanvas-header"></slot>
      <button type="button" class="btn-close" @click="showOffcanvas = false"></button>
    </template>

    <slot name="offcanvas-body">
      <div class="card bg-grey-100 text-white position-sticky bg-opacity-75">
        <div class="card-header">
          <h5 class="mb-0">{{ project?.title }}</h5>
        </div>

        <div class="card-body">
          <p>{{ project?.title }}</p>
        </div>
      </div>
    </slot>
  </BOffcanvas>
</template>

<style scoped lang="scss">

</style>