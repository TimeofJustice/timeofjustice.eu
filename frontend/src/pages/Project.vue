<script setup lang="ts">
import { Project } from "../types/Project.vue";
import ProjectDetails from "./Projects/ProjectDetails.vue";

interface Props {
  project: Project;
}

defineProps<Props>();
</script>

<template>
  <div class="container">
    <ProjectDetails project="project" />
  </div>
</template>

<style scoped lang="scss">

</style>