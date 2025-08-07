<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { ref } from "vue";
import ProfileCard from "@components/ProfileCard.vue";
import ProjectDetails from "@pages/Projects/ProjectDetails.vue";
import { Social } from "@/types/Social.ts";
import { Project } from "@/types/Project.ts";
import ProjectItem from "@pages/Projects/ProjectItem.vue";
import { Tool } from "@/types/Tool.ts";
import { TranslatedText } from "@/types/TranslatedText.ts";

interface Props {
  profile?: {
    picture?: string;
    description?: TranslatedText;
    shortDescription?: TranslatedText;
    repo?: string;
  };
  socials: Social[];
  projects: Project[];
  tools: Tool[];
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

  <div class="d-flex container-xxl gap-4 flex-column flex-lg-row">
    <div
      class="col-md-4 flex-grow-0 justify-content-start align-items-end d-none d-lg-flex flex-column"
    >
      <!-- If you found this, keep this our dirty little secret -->
      <h1 class="display-1 fw-bold invisible" style="line-height: 50px">
        {{ $t("index.title.top") }}
        <br />
        <span class="display-1 fw-bold text-tertiary">{{
          $t("index.title.bottom")
        }}</span>
      </h1>
      <ProfileCard
        :profile-picture="profile?.picture"
        :description="profile?.description"
        :short-description="profile?.shortDescription"
        :repo="profile?.repo"
        :socials="socials"
        :known-tools="tools"
        class="position-sticky profile"
      />
    </div>
    <div class="d-flex flex-grow-1 justify-content-center d-block d-lg-none">
      <ProfileCard
        :profile-picture="profile?.picture"
        :description="profile?.description"
        :short-description="profile?.shortDescription"
        :repo="profile?.repo"
        :socials="socials"
        :known-tools="tools"
        variant="small"
      />
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
            :callback="loadProject"
            :key="i"
          />
        </div>
      </section>
    </div>
  </div>

  <BOffcanvas v-model="showOffcanvas" placement="end">
    <template #header>
      <div class="d-flex w-100 gap-2">
        <BButton
          variant="tertiary"
          class="btn-square"
          @click="showOffcanvas = false"
        >
          <iconify-icon icon="ep:close-bold" />
        </BButton>
        <BButton
          variant="tertiary"
          class="btn-square"
          :to="`/project/${project?.id}`"
          :title="$t('general.more')"
          target="_blank"
          external
        >
          <iconify-icon icon="pajamas:external-link" />
        </BButton>
      </div>
    </template>

    <slot name="offcanvas-body">
      <ProjectDetails :project="project" />
    </slot>
  </BOffcanvas>
</template>

<style scoped lang="scss">
.profile {
  top: 0.5rem;

  @media (max-width: 1400px) {
    top: 4rem;
  }
}
</style>
