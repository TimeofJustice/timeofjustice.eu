<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { Social } from "@/types/Social.ts";
import { Project } from "@/types/Project.ts";
import { Tool } from "@/types/Tool.ts";
import { Profile } from "@/types/Profile.ts";

import ProfileCard from "@components/ProfileCard.vue";
import ProjectListItem from "@components/ProjectListItem.vue";
import ProfileRepositoryCard from "@components/ProfileRepositoryCard.vue";
import ProfileToolsCard from "@components/ProfileToolsCard.vue";

interface ProjectsPageProps {
  profile?: Profile;
  socials: Social[];
  tools: Tool[];
  projects: Project[];
}

defineProps<ProjectsPageProps>();
</script>

<template>
  <Head title="Projects" />

  <div class="d-flex container-xxl gap-2 flex-column flex-lg-row mb-2">
    <div
      class="col-lg-4 flex-grow-0 justify-content-start align-items-lg-end d-flex flex-column"
    >
      <!-- If you found this, keep this our dirty little secret -->
      <h1 class="d-flex flex-column display-1 lh-1 d-none d-lg-flex invisible">
        <span class="fw-bold">
          {{ $t("index.title.top") }}
        </span>
        <span class="fw-bold text-tertiary">
          {{ $t("index.title.bottom") }}
        </span>
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

    <div class="d-flex flex-column h-100 flex-grow-1 flex-shrink-1 gap-2">
      <section v-motion-slide-visible-once-top>
        <h1 class="d-flex flex-column display-1 lh-1">
          <span class="fw-bold">
            {{ $t("index.title.top") }}
          </span>
          <span class="fw-bold text-tertiary">
            {{ $t("index.title.bottom") }}
          </span>
        </h1>
        <div class="d-flex flex-column gap-2">
          <ProjectListItem
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
