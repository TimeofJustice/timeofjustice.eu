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
  <BCard
    body-class="w-100 w-lg-auto d-flex flex-lg-column align-items-lg-center gap-2"
  >
    <v-lazy-image
      class="img-fluid rounded-circle w-75 profile-image"
      :src="profile?.picture || DefaultProfileImage"
      :alt="$t('profile.picture_alt')"
    />

    <div
      class="d-flex flex-column justify-content-between align-items-lg-center gap-2"
    >
      <div>
        <h5 class="fw-bold mb-0">TimeofJustice</h5>
        <span
          class="text-accent d-flex justify-content-lg-center align-items-center gap-1"
        >
          <small class="text-accent">Jonas Oelschner</small>
          <i class="fi fi-de rounded-1" :title="$t('index.profile.based_in')" />
        </span>
      </div>

      <small class="d-none d-lg-block text-lg-center">
        {{ profile?.description }}
      </small>

      <small class="d-block d-lg-none">
        {{ profile?.shortDescription }}
      </small>

      <div class="d-flex gap-2">
        <BLink
          :title="social?.title || social.icon"
          :href="social.url"
          target="_blank"
          v-for="social in socials"
          :key="social.icon"
        >
          <h4 class="mb-0 opacity-75">
            <iconify-icon :icon="social.icon" />
          </h4>
        </BLink>
      </div>
    </div>
  </BCard>
</template>

<style scoped lang="scss">
.profile-image {
  width: 75%;
  aspect-ratio: 1 / 1;

  @media (max-width: 992px) {
    min-width: 6rem;
    max-width: 8rem;
  }
}
</style>
