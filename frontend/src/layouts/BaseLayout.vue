<script setup lang="ts">
import BaseNavbar from "@components/BaseNavbar.vue";
import GamesWalletSettingsModal from "@components/GamesWalletSettingsModal.vue";
import { ref } from "@node_modules/vue";
import { shallowRef, watch } from "vue";
import { router } from "@inertiajs/vue3";
import { OffcanvasState } from "@/types/OffcanvasState.ts";

import LizardAudio from "@assets/audio/lizard.wav";

interface BaseLayoutProps {
  production: boolean;
  stable: boolean;
  navbarSize?: "normal" | "small";
  offcanvasState?: OffcanvasState;
}

const { offcanvasState } = defineProps<BaseLayoutProps>();

const showOffcanvas = ref(false);
const offcanvasComponent = shallowRef<string | null>(
  (offcanvasState && offcanvasState.component) || null,
);

const showStableHint = ref(true);

watch(
  () => offcanvasState,
  (newOffcanvasState) => {
    if (!newOffcanvasState) {
      showOffcanvas.value = false;
      offcanvasComponent.value = null;
      return;
    }

    showOffcanvas.value = true;

    import(`@/pages/${newOffcanvasState.component}.vue`)
      .then((module) => {
        offcanvasComponent.value = module.default;
      })
      .catch((error) => {
        console.error(
          `Failed to load component ${newOffcanvasState.component}:`,
          error,
        );
        offcanvasComponent.value = null;
      });
  },
  { immediate: true },
);

const lizardAudio = ref<HTMLAudioElement | null>(null);

const playLizardSound = () => {
  if (lizardAudio.value) {
    lizardAudio.value.currentTime = 0;
    lizardAudio.value.play();
  }
};
</script>

<template>
  <div class="absolute inset-0 flex flex-col overflow-hidden">
    <div
      class="absolute inset-0 flex h-screen w-screen items-center justify-center bg-space-blue"
    >
      <div class="gradient"></div>
      <template v-if="$i18n.locale === 'yoda'">
        <div class="x-wing" v-for="i in 5" :key="i">
          <i class="fi fi-x-wing"></i>
        </div>
      </template>
    </div>

    <div
      class="content-body relative z-0 flex w-full grow flex-col overflow-x-hidden overflow-y-auto"
    >
      <BaseNavbar :size="navbarSize" />

      <slot></slot>

      <UiOffcanvas
        v-model="showOffcanvas"
        placement="end"
        class="w-200"
        body-class="px-0"
        @hidden="
          router.visit(offcanvasState?.source || '/', {
            only: ['offcanvasState'],
            preserveState: true,
            preserveScroll: true,
          })
        "
      >
        <template #header>
          <div class="flex w-full gap-2">
            <UiButton
              variant="tertiary"
              square
              :title="$t('general.close')"
              @click="showOffcanvas = false"
            >
              <iconify-icon icon="ep:close-bold" />
            </UiButton>
            <UiButton
              variant="tertiary"
              square
              :to="$page.url"
              :title="$t('general.more')"
              target="_blank"
              external
            >
              <iconify-icon icon="pajamas:external-link" />
            </UiButton>
            <UiButton
              variant="tertiary"
              square
              :title="$t('easter_egg.lizard')"
              @click="playLizardSound"
            >
              <iconify-icon icon="fluent-emoji-high-contrast:lizard" />
            </UiButton>
            <audio class="hidden" ref="lizardAudio">
              <source :src="LizardAudio" type="audio/wav" />
            </audio>
          </div>
        </template>

        <slot name="offcanvas-body">
          <component
            :is="offcanvasComponent || 'div'"
            v-bind="offcanvasState?.props"
            v-if="offcanvasComponent"
          />
        </slot>
      </UiOffcanvas>

      <div class="fixed inset-x-0 bottom-0 z-3 container-fixed" v-if="!stable">
        <UiAlert v-model="showStableHint" variant="info" dismissible>
          <template #close>
            <iconify-icon icon="ep:close-bold" />
          </template>

          <vue-markdown :source="$t('nav.stable_hint')" />
        </UiAlert>
      </div>
    </div>

    <GamesWalletSettingsModal />

    <UiToaster />
  </div>
</template>

<style scoped>
@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.gradient {
  --size: 100vh;

  width: var(--size);
  height: var(--size);

  filter: blur(calc(var(--size) / 7));
  background-image: linear-gradient(hsl(222 84% 60%), hsl(164 79% 71%));
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;

  animation: rotate 50s linear infinite;
}

@keyframes fall {
  to {
    transform: translate3d(-30em, 10em, 0);
  }
}

/* Values are fixed rather than random so every render looks the same. */
.x-wing {
  position: absolute;
  top: var(--top-offset);
  left: 0;

  transform: translate3d(150em, -50em, 0);
  animation: fall var(--fall-duration) var(--fall-delay) linear infinite;
}

.x-wing:nth-child(1) {
  --top-offset: 63vh;
  --fall-duration: 7.4s;
  --fall-delay: 1.2s;
}
.x-wing:nth-child(2) {
  --top-offset: 92vh;
  --fall-duration: 10.8s;
  --fall-delay: 6.5s;
}
.x-wing:nth-child(3) {
  --top-offset: 51vh;
  --fall-duration: 8.1s;
  --fall-delay: 3.9s;
}
.x-wing:nth-child(4) {
  --top-offset: 78vh;
  --fall-duration: 11.6s;
  --fall-delay: 9.1s;
}
.x-wing:nth-child(5) {
  --top-offset: 69vh;
  --fall-duration: 6.3s;
  --fall-delay: 0.4s;
}
</style>

<style>
.content-body {
  scrollbar-gutter: stable both-edges;
}

.content-body:has(.fullscreen) {
  scrollbar-gutter: auto;
}
</style>
