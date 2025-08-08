<script setup lang="ts">
import BaseNavbar from "@components/BaseNavbar.vue";

interface BaseLayoutProps {
  production: boolean;
  stable: boolean;
  navbarSize?: "normal" | "small";
}

defineProps<BaseLayoutProps>();
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
