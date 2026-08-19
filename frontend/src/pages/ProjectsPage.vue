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

  <div class="container-page mb-2 flex flex-col gap-2 lg:flex-row">
    <div
      class="flex grow-0 flex-col justify-start lg:w-1/3 lg:shrink-0 lg:items-end"
    >
      <!-- If you found this, keep this our dirty little secret -->
      <h1
        class="invisible hidden flex-col text-display-1-fluid leading-none font-light xl:text-display-1 lg:flex"
      >
        <span class="font-bold">
          {{ $t("index.title.top") }}
        </span>
        <span class="font-bold text-tertiary">
          {{ $t("index.title.bottom") }}
        </span>
      </h1>
      <div class="profile sticky flex flex-col gap-2">
        <ProfileCard
          :profile="profile"
          :socials="socials"
          :known-tools="tools"
        />
        <ProfileToolsCard
          :tools="tools"
          v-if="tools.length"
          class="hidden lg:block"
        />
        <ProfileRepositoryCard
          :repository="profile?.repository"
          v-if="profile?.repository"
          class="hidden lg:block"
        />
      </div>
    </div>

    <div class="flex h-full shrink grow flex-col gap-2">
      <section v-motion-slide-visible-once-top>
        <h1
          class="flex flex-col text-display-1-fluid leading-none font-light xl:text-display-1"
        >
          <span class="font-bold">
            {{ $t("index.title.top") }}
          </span>
          <span class="font-bold text-tertiary">
            {{ $t("index.title.bottom") }}
          </span>
        </h1>
        <div class="flex flex-col gap-2">
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

<style scoped>
.profile {
  top: 0.5rem;
  max-width: 18rem;
}

@media (max-width: 1400px) {
  .profile {
    top: 4rem;
  }
}

@media (max-width: 992px) {
  .profile {
    max-width: 100%;
  }
}
</style>
