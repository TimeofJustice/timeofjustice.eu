<script setup lang="ts">
import { Social } from "@/types/Social.ts";
import { Profile } from "@/types/Profile.ts";

import DefaultProfileImage from "@assets/images/TimeofJustice.svg";

interface ProfileCardProps {
  profile?: Profile;
  socials: Social[];
}

defineProps<ProfileCardProps>();
</script>

<template>
  <UiCard body-class="flex w-full gap-2 lg:w-auto lg:flex-col lg:items-center">
    <v-lazy-image
      class="profile-image h-auto max-w-full rounded-full"
      :src="profile?.picture || DefaultProfileImage"
      :alt="$t('profile.picture_alt')"
    />

    <div class="flex flex-col justify-between gap-2 lg:items-center">
      <div>
        <h5 class="mb-0 font-bold">TimeofJustice</h5>
        <span class="flex items-center gap-1 text-accent lg:justify-center">
          <small class="text-accent">Jonas Oelschner</small>
          <i
            class="fi fi-de rounded-sm"
            :title="$t('index.profile.based_in')"
          />
        </span>
      </div>

      <small class="hidden lg:block lg:text-center">
        {{ profile?.description }}
      </small>

      <small class="block lg:hidden">
        {{ profile?.shortDescription }}
      </small>

      <div class="flex gap-2">
        <UiLink
          :title="social?.title || social.icon"
          :href="social.url"
          target="_blank"
          external
          v-for="social in socials"
          :key="social.icon"
        >
          <h4 class="mb-0 opacity-75">
            <iconify-icon :icon="social.icon" />
          </h4>
        </UiLink>
      </div>
    </div>
  </UiCard>
</template>

<style scoped>
.profile-image {
  width: 75%;
  aspect-ratio: 1 / 1;
}

@media (max-width: 992px) {
  .profile-image {
    min-width: 6rem;
    max-width: 8rem;
  }
}
</style>
