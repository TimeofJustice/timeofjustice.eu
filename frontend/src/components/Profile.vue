<script setup lang="ts">
import { Social } from "@/types/Social.ts";
import { Vue3Marquee } from "@node_modules/vue3-marquee";
import { Tool } from "@/types/Tool.ts";
import toolContainer from "@components/Profile/Tool.vue";
import { TranslatedText } from "@/types/TranslatedText.ts";

interface Props {
  profilePicture?: string;
  description?: TranslatedText;
  shortDescription?: TranslatedText;
  repo?: string;
  socials: Social[];
  knownTools: Tool[];
  variant?: "small" | "large";
}

withDefaults(defineProps<Props>(), {
  variant: "large",
  profilePicture: undefined,
  description: undefined,
  shortDescription: undefined,
});
</script>

<template>
  <div class="d-flex flex-column gap-2" v-if="variant === 'large'">
    <div class="card text-light blur-box border-0">
      <div
        class="card-body d-flex flex-column align-items-center gap-2"
        style="max-width: 18rem"
      >
        <img
          class="img-fluid rounded-circle w-75"
          :src="profilePicture || require('@assets/images/TimeofJustice.svg')"
          alt="TimeofJustice"
        />

        <div class="text-center">
          <h5 class="fw-bold text-center mb-0">TimeofJustice</h5>
          <small class="text-grey-10"> Jonas Oelschner </small>
          <i
            class="fi fi-de rounded-1"
            :title="$t('index.profile.based_in')"
          ></i>
        </div>

        <small class="text-center mb-0">
          {{ description && description[$i18n.locale as keyof TranslatedText] }}
        </small>

        <div class="d-flex gap-2">
          <a
            class="link"
            :title="$t(`socials.${social.type}`)"
            :href="social.url"
            target="_blank"
            v-for="social in socials"
            :key="social.type"
          >
            <h4 class="mb-0 opacity-75">
              <font-awesome-icon :icon="social.icon" />
            </h4>
          </a>
        </div>
      </div>
    </div>

    <div
      class="blur-box rounded-1 py-2 overflow-hidden"
      style="height: 3rem"
      v-if="knownTools.length"
    >
      <Vue3Marquee
        class="gradient-carousel h-100"
        style="max-width: 18rem"
        pause-on-hover
        clone
      >
        <tool-container :tool="tool" v-for="tool in knownTools" />
      </Vue3Marquee>
    </div>

    <div
      class="card blur-box text-light border-0 overflow-hidden"
      style="max-width: 18rem"
      v-if="repo"
    >
      <div class="card-body d-flex flex-column gap-3">
        <h5 class="mb-0">{{ $t("index.profile.working_on") }}</h5>

        <img
          class="img-fluid"
          style="max-width: 18rem"
          :src="repo"
          alt="timeofjustice"
        />
      </div>
    </div>
  </div>

  <div
    class="card bg-grey-100 text-light bg-opacity-50 border-0 shadow d-flex w-100"
    v-else
  >
    <div class="card-body d-flex gap-3">
      <div
        class="d-flex justify-content-center align-items-center"
        style="min-width: 6rem; max-width: 8rem"
      >
        <img
          class="img-fluid rounded-circle"
          :src="profilePicture || require('@assets/images/TimeofJustice.svg')"
          alt="TimeofJustice"
        />
      </div>

      <div
        class="d-flex flex-column gap-2 h-100 justify-content-between flex-shrink-1"
      >
        <div class="d-flex flex-column gap-1">
          <div>
            <h5 class="card-title mb-0">TimeofJustice</h5>
            <small class="text-grey-10"> Jonas Oelschner </small>
            <i
              class="fi fi-de rounded-1"
              :title="$t('index.profile.based_in')"
            ></i>
          </div>

          <small>
            {{
              shortDescription &&
              shortDescription[$i18n.locale as keyof TranslatedText]
            }}
          </small>
        </div>

        <div class="d-flex gap-2">
          <a
            class="link"
            :title="$t(`socials.${social.type}`)"
            :href="social.url"
            target="_blank"
            v-for="social in socials"
            :key="social.type"
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

<style scoped lang="scss">
.gradient-carousel {
  mask-image: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0),
    rgba(0, 0, 0, 1) 15%,
    rgba(0, 0, 0, 1) 85%,
    rgba(0, 0, 0, 0)
  );
}
</style>
