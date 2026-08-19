<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { ROUTES } from "@configurations/routes.ts";

import LocaleDropdown from "@components/LocaleDropdown.vue";
import BaseNavbarLink from "@components/BaseNavbarLink.vue";

import TimeofJusticeLogo from "@assets/images/TimeofJustice.svg";

interface BaseNavbarProps {
  size?: "normal" | "small";
}

const { size = "normal" } = defineProps<BaseNavbarProps>();

const isScrolled = ref(false);
const showNavOffcanvas = ref(false);

onMounted(() => {
  const parent: HTMLElement =
    document.querySelector(".content-body") ?? document.documentElement;
  const onScroll = () => {
    isScrolled.value = parent.scrollTop > 0;
  };

  parent.addEventListener("scroll", onScroll);

  onUnmounted(() => {
    parent.removeEventListener("scroll", onScroll);
  });
});
</script>

<template>
  <div
    class="pointer-events-none top-0 z-1 flex w-full flex-wrap content-center items-center justify-center py-2 lg:flex-nowrap"
    :class="size === 'small' ? 'absolute' : 'sticky'"
  >
    <div
      class="navbar-body pointer-events-auto container-page flex flex-row items-center justify-between gap-2"
      :class="{
        'scrolled relative min-w-0 rounded-md bg-card shadow-card backdrop-blur-card':
          isScrolled || size === 'small',
      }"
    >
      <UiButton
        variant="tertiary"
        square
        class="text-control-lg leading-none lg:hidden"
        @click="showNavOffcanvas = true"
      >
        <iconify-icon icon="fa6-solid:bars" />
      </UiButton>

      <div class="flex items-center">
        <LocaleDropdown class="block lg:hidden" />

        <div class="py-1.25 text-control-lg whitespace-nowrap">
          <v-lazy-image
            class="brand-picture h-auto max-w-full rounded-md"
            :src="TimeofJusticeLogo"
            :alt="$t('nav.brand_alt')"
          />
        </div>
      </div>

      <div class="hidden w-full items-center justify-between lg:flex">
        <div class="flex items-center">
          <BaseNavbarLink
            :route="route"
            v-for="route in ROUTES"
            :key="route.name"
          />
        </div>

        <LocaleDropdown />
      </div>
    </div>

    <div class="pointer-events-auto flex lg:hidden">
      <UiOffcanvas
        v-model="showNavOffcanvas"
        placement="start"
        class="w-full sm:w-75"
        :teleport-disabled="true"
      >
        <template #header>
          <UiButton
            variant="tertiary"
            square
            :title="$t('general.close')"
            @click="showNavOffcanvas = false"
          >
            <iconify-icon icon="ep:close-bold" />
          </UiButton>
        </template>

        <div class="flex flex-col" @click="showNavOffcanvas = false">
          <BaseNavbarLink
            :route="route"
            v-for="route in ROUTES"
            :key="route.name"
          />
        </div>
      </UiOffcanvas>
    </div>
  </div>
</template>

<style scoped>
.brand-picture {
  width: 2.3rem;
  min-width: 2.3rem;
  height: 2.3rem;
  min-height: 2.3rem;
}

/*
 * On scroll the bar collapses into a compact pill. Below xxl there is no room
 * for that, so only the surface treatment changes.
 */
.navbar-body {
  margin: 0;
  border-radius: 0.5rem;

  transition:
    backdrop-filter 0.3s ease-in-out,
    background 0.3s ease-in-out,
    box-shadow 0.3s ease-in-out,
    padding 0.3s ease-in-out,
    margin 0.3s ease-in-out;
}

.navbar-body.scrolled {
  padding-left: 0.3125rem;
  padding-right: 0.3125rem;
  margin-left: 0.4375rem;
  margin-right: 0.4375rem;

  width: 26rem;
}

@media (max-width: 1400px) {
  .navbar-body.scrolled {
    width: 100%;
  }
}

@media (min-width: 1400px) {
  .navbar-body {
    transition:
      width 0.8s cubic-bezier(0.68, -0.55, 0.27, 1.55),
      backdrop-filter 0.3s ease-in-out,
      background 0.3s ease-in-out,
      box-shadow 0.3s ease-in-out,
      padding 0.3s ease-in-out,
      margin 0.3s ease-in-out;
  }

  .navbar-body :deep(.link-title) {
    max-width: 10rem;
    overflow: hidden;

    transition: max-width 0.3s ease-in-out;
    transition-delay: 0.2s;
  }

  .navbar-body.scrolled :deep(.link-title) {
    max-width: 0;
    transition-delay: 0s;
  }
}
</style>
