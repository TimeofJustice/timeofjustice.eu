<script setup lang="ts">
import { Project } from "../types/Project.ts";
import ProjectDetails from "./Projects/ProjectDetails.vue";
import { Head } from "@inertiajs/vue3";

interface Props {
  project: Project;
}

defineProps<Props>();
</script>

<template>
  <Head :title="project.title" />

  <div class="container">
    <ProjectDetails :project="project" />
  </div>
</template>

<style scoped lang="scss"></style>
