<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { Social } from "@/types/Social.ts";
import { Project } from "@/types/Project.ts";
import { Tool } from "@/types/Tool.ts";
import { Profile } from "@/types/Profile.ts";

import ProfileCard from "@components/ProfileCard.vue";
import ProjectItem from "@pages/Projects/ProjectItem.vue";
import ProfileRepositoryCard from "@components/ProfileRepositoryCard.vue";
import ProfileToolsCard from "@components/ProfileToolsCard.vue";

interface Props {
  profile?: Profile;
  socials: Social[];
  projects: Project[];
  tools: Tool[];
}

defineProps<Props>();
</script>

<template>
  <Head title="Projects" />

  <div class="d-flex container-xxl gap-4 flex-column flex-lg-row">
    <div
      class="col-lg-4 flex-grow-0 justify-content-start align-items-lg-end d-flex flex-column"
    >
      <!-- If you found this, keep this our dirty little secret -->
      <h1
        class="display-1 fw-bold invisible d-none d-lg-block"
        style="line-height: 50px"
      >
        {{ $t("index.title.top") }}
        <br />
        <span class="display-1 fw-bold text-tertiary">{{
          $t("index.title.bottom")
        }}</span>
      </h1>
      <div class="profile position-sticky d-flex flex-column gap-2">
        <ProfileCard
          :profile="profile"
          :socials="socials"
          :known-tools="tools"
        />
        <ProfileToolsCard
          :tools="tools"
          v-if="tools.length"
          class="d-none d-lg-block"
        />
        <ProfileRepositoryCard
          :repository="profile?.repository"
          v-if="profile?.repository"
          class="d-none d-lg-block"
        />
      </div>
    </div>

    <div
      class="d-flex flex-column h-100 flex-grow-1 flex-shrink-1 gap-2"
      style="min-width: 0"
    >
      <section v-motion-slide-visible-once-top v-if="true">
        <h1 class="display-1 fw-bold" style="line-height: 50px">
          {{ $t("index.title.top") }}
          <br />
          <span class="display-1 fw-bold text-tertiary">{{
            $t("index.title.bottom")
          }}</span>
        </h1>
        <div class="d-flex flex-column gap-3 mb-3">
          <ProjectItem
            :project="project"
            v-for="(project, i) in projects"
            :key="i"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.profile {
  top: 0.5rem;
  max-width: 18rem;

  @media (max-width: 1400px) {
    top: 4rem;
  }

  @media (max-width: 992px) {
    max-width: 100%;
  }
}
</style>
