<script setup lang="ts">
import BaseNavbar from "@components/BaseNavbar.vue";
import { ref } from "@node_modules/vue";
import { shallowRef, watch } from "vue";
import { router } from "@inertiajs/vue3";
import { OffcanvasState } from "@/types/OffcanvasState.ts";

import LizardAudio from "@assets/audio/lizard.wav";
import TAlert from "@/components/TAlert.vue";

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
      class="absolute inset-0 flex items-center justify-center bg-space-blue w-screen h-screen"
    >
      <div class="gradient"></div>
      <template v-if="$i18n.locale === 'yoda'">
        <div class="x-wing" v-for="i in 5" :key="i">
          <i class="fi fi-x-wing"></i>
        </div>
      </template>
    </div>

    <div
      class="relative z-0 flex flex-col flex-1 overflow-y-auto overflow-x-hidden"
    >
      <BaseNavbar :size="navbarSize" />

      <slot />

      <div
        class="container fixed bottom-0 inset-s-0 inset-e-0 z-3 mx-auto max-w-7xl px-2 sm:px-6 lg:px-8 mb-2"
        v-if="stable"
      >
        <TAlert :model-value="true">
          <vue-markdown :source="$t('nav.stable_hint')" class="flex-1" />
        </TAlert>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
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
  --speed: 50s;
  --easing: linear;

  width: var(--size);
  height: var(--size);
  filter: blur(calc(var(--size) / 7));
  background-image: linear-gradient(
    hsl(222, 84%, 60%, 100%),
    hsl(164, 79%, 71%)
  );
  animation: rotate var(--speed) var(--easing) infinite;
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
}

body {
  background-color: #071c39;
}

@function random_range($min, $max) {
  $rand: random();
  $random_range: $min + floor($rand * (($max - $min) + 1));
  @return $random_range;
}

.x-wing {
  $count: 50;
  --fall-duration: 9s;

  position: absolute;
  top: var(--top-offset);
  left: 0;
  transform: translate3d(150em, -50em, 0);
  animation: fall var(--fall-duration) var(--fall-delay) linear infinite;

  @for $i from 1 through $count {
    &:nth-child(#{$i}) {
      --star-tail-length: #{random_range(500em, 750em) / 100};
      --top-offset: #{random_range(5000vh, 10000vh) / 100};
      --fall-duration: #{random_range(6000, 12000s) / 1000};
      --fall-delay: #{random_range(0, 10000s) / 1000};
    }
  }
}

@keyframes fall {
  to {
    transform: translate3d(-30em, 10em, 0);
  }
}
</style>
