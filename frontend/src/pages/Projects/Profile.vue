<script setup lang="ts">
import { Social } from "@/types/Social.ts";

interface Props {
  socials: Social[];
  variant?: 'small' | 'large';
}

withDefaults(defineProps<Props>(), {
  variant: 'large',
});
</script>

<template>
  <div class="d-flex flex-column gap-2" v-if="variant === 'large'">
    <div class="card bg-grey-100 text-light bg-opacity-50 border-0 shadow">
      <div class="card-body d-flex flex-column align-items-center gap-2" style="max-width: 18rem">
        <img class="img-fluid rounded-circle w-75" :src="require('@assets/images/TimeofJustice.svg')" alt="TimeofJustice">

        <div class="text-center">
          <h5 class="fw-bold text-center mb-0">
            TimeofJustice
          </h5>
          <small class="text-grey-10">
            Jonas Oelschner
          </small>
          <i class="fi fi-de rounded-1" :title="$t('index.profile.based_in')"></i>
        </div>

        <small class="text-center mb-0">
          {{ $t("index.profile.description") }}
        </small>

        <div class="d-flex gap-2">
          <a
            class="link"
            :title="$t(`socials.${social.type}`)"
            :href="social.url"
            target="_blank"
            v-for="social in socials" :key="social.type"
          >
            <h4 class="mb-0 opacity-75">
              <font-awesome-icon :icon="social.icon" />
            </h4>
          </a>
        </div>
      </div>
    </div>

    <div class="card bg-grey-100 text-light bg-opacity-50 border-0 shadow" style="max-width: 18rem">
      <div class="card-body d-flex flex-column gap-3">
        <h5 class="mb-0">{{ $t('index.profile.working_on') }}</h5>

        <img class="img-fluid" style="max-width: 18rem" src="https://github-readme-stats.vercel.app/api/pin/?username=timeofjustice&repo=timeofjustice.eu&theme=github_dark_dimmed" alt="timeofjustice" />
      </div>
    </div>
  </div>

  <div class="card bg-grey-100 text-light bg-opacity-50 border-0 shadow d-flex w-100" v-else>
    <div class="card-body d-flex gap-3">
      <div class="d-flex justify-content-center align-items-center" style="min-width: 6rem; max-width: 8rem;">
        <img class="img-fluid rounded-circle" :src="require('@assets/images/TimeofJustice.svg')" alt="TimeofJustice">
      </div>

      <div class="d-flex flex-column gap-2 h-100 justify-content-between flex-shrink-1">
        <div class="d-flex flex-column gap-1">
          <div>
            <h5 class="card-title mb-0">TimeofJustice</h5>
            <small class="text-grey-10">
              Jonas Oelschner
            </small>
            <i class="fi fi-de rounded-1" :title="$t('index.profile.based_in')"></i>
          </div>

          <small>
            {{ $t("index.profile.description_short") }}
          </small>
        </div>

        <div class="d-flex gap-2">
          <a
            class="link"
            :title="$t(`socials.${social.type}`)"
            :href="social.url"
            target="_blank"
            v-for="social in socials" :key="social.type"
          >
            <h4 class="mb-0 opacity-75">
              <font-awesome-icon :icon="social.icon" />
            </h4>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>