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
    class="navbar navbar-expand-lg top-0 z-1 w-100 d-flex align-content-center justify-content-center pe-none"
    :class="{
      'position-absolute': size === 'small',
      'position-sticky': size === 'normal',
    }"
  >
    <div
      class="container-xxl navbar-body pe-auto gap-2 flex-row"
      :class="{ 'scrolled card': isScrolled || size === 'small' }"
    >
      <BNavbarToggle
        target="nav-offcanvas"
        class="btn btn-tertiary btn-square navbar-toggler border-0"
      >
        <iconify-icon icon="fa6-solid:bars" />
      </BNavbarToggle>

      <div class="d-flex align-items-center">
        <LocaleDropdown class="d-block d-lg-none" />

        <BNavbarBrand class="me-0">
          <v-lazy-image
            class="img-fluid rounded brand-picture"
            :src="TimeofJusticeLogo"
            :alt="$t('nav.brand_alt')"
          />
        </BNavbarBrand>
      </div>

      <BNavbarNav
        class="d-none d-lg-flex justify-content-between align-items-center w-100"
      >
        <div class="d-flex align-items-center ps-0 pt-0">
          <BaseNavbarLink
            :route="route"
            v-for="route in ROUTES"
            :key="route.name"
          />
        </div>

        <LocaleDropdown />
      </BNavbarNav>
    </div>

    <div class="pe-auto d-flex d-lg-none">
      <BOffcanvas
        id="nav-offcanvas"
        placement="start"
        is-nav
        class="offcanvas-sm-small"
        header-close-variant="tertiary"
        header-close-class="btn-square ms-0"
        :teleport-disabled="true"
      >
        <template #header-close>
          <iconify-icon icon="ep:close-bold" />
        </template>

        <BNavbarNav>
          <BaseNavbarLink
            :route="route"
            v-for="route in ROUTES"
            :key="route.name"
          />
        </BNavbarNav>
      </BOffcanvas>
    </div>
  </div>
</template>

<style scoped lang="scss">
.brand-picture {
  width: 2.3rem;
  min-width: 2.3rem;
  height: 2.3rem;
  min-height: 2.3rem;
}
</style>
