<script setup lang="ts">
import BaseNavbar from "@components/BaseNavbar.vue";
import { ref } from "@node_modules/vue";
import { shallowRef, watch } from "vue";
import { router } from "@inertiajs/vue3";

interface BaseLayoutProps {
  production: boolean;
  stable: boolean;
  navbarSize?: "normal" | "small";
  offcanvasComponent?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  offcanvasProps?: Record<string, any>;
  offcanvasSource?: string;
}

const { offcanvasComponent } = defineProps<BaseLayoutProps>();

const showOffcanvas = ref(false);
const _offcanvasComponent = shallowRef<string | null>(
  offcanvasComponent || null,
);

watch(
  () => offcanvasComponent,
  (newVal) => {
    showOffcanvas.value = !!newVal;

    if (!newVal) {
      _offcanvasComponent.value = null;
      return;
    }

    import(`@/pages/${newVal}.vue`)
      .then((module) => {
        _offcanvasComponent.value = module.default;
      })
      .catch((error) => {
        console.error(`Failed to load component ${newVal}:`, error);
        _offcanvasComponent.value = null; // Fallback if the component fails to load
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
  <div
    class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column overflow-hidden"
  >
    <div
      class="position-absolute top-0 bottom-0 start-0 end-0 d-flex justify-content-center align-items-center bg-space-blue vw-100 vh-100"
    >
      <div class="gradient"></div>
      <template v-if="$i18n.locale === 'yoda'">
        <div class="x-wing" v-for="i in 5" :key="i">
          <i class="fi fi-x-wing"></i>
        </div>
      </template>
    </div>

    <div
      class="content-body w-100 z-0 flex-grow-1 d-flex flex-column overflow-y-auto overflow-x-hidden position-relative"
    >
      <BaseNavbar :size="navbarSize" />

      <slot></slot>

      <BOffcanvas
        v-model="showOffcanvas"
        placement="end"
        @hide="
          router.visit(offcanvasSource || '/', {
            only: ['offcanvasComponent', 'offcanvasProps', 'offcanvasSource'],
            preserveState: true,
            preserveScroll: true,
          })
        "
      >
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
              :to="`/projects/${offcanvasProps?.project?.id}`"
              :title="$t('general.more')"
              target="_blank"
              external
            >
              <iconify-icon icon="pajamas:external-link" />
            </BButton>
            <BButton
              variant="tertiary"
              class="btn-square"
              :title="$t('easter_egg.lizard')"
              @click="playLizardSound"
            >
              <iconify-icon icon="fluent-emoji-high-contrast:lizard" />
            </BButton>
            <audio class="d-none" ref="lizardAudio">
              <source
                :src="require('@assets/audio/lizard.wav')"
                type="audio/wav"
              />
            </audio>
          </div>
        </template>

        <slot name="offcanvas-body">
          <component
            :is="_offcanvasComponent || 'div'"
            v-bind="offcanvasProps"
            v-if="offcanvasComponent"
          >
          </component>
        </slot>
      </BOffcanvas>

      <div
        class="container position-fixed bottom-0 start-0 end-0 z-3"
        v-if="!stable"
      >
        <BAlert
          :model-value="true"
          variant="info"
          dismissible
          close-variant="tertiary"
          close-class="btn-square"
        >
          <template #close>
            <iconify-icon icon="ep:close-bold" />
          </template>

          <vue-markdown :source="$t('nav.stable_hint')" />
        </BAlert>
      </div>
    </div>
  </div>
</template>
