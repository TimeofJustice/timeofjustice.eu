<script setup lang="ts">
import { faBars } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@node_modules/@fortawesome/vue-fontawesome";
import LocaleDropdown from "@components/LocaleDropdown.vue";
import { onMounted, onUnmounted, ref } from "vue";
import NavLinks from "@layouts/components/NavLinks.vue";

interface IBasicLayout {
  small?: boolean;
}

defineProps<IBasicLayout>();

// Check if the page is scrolled
const isScrolled = ref(false);
onMounted(() => {
  const parent: HTMLElement = document.querySelector(".content-body")!;
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
    :class="{ 'position-absolute': small, 'position-sticky': !small }"
  >
    <div
      class="container-xxl navbar-body pe-auto gap-2 flex-row"
      :class="{ 'scrolled card': isScrolled || small }"
    >
      <BNavbarToggle
        target="nav-offcanvas"
        class="btn btn-tertiary btn-square navbar-toggler border-0"
      >
        <FontAwesomeIcon :icon="faBars" />
      </BNavbarToggle>

      <div class="d-flex align-items-center">
        <LocaleDropdown class="d-block d-lg-none" />

        <BNavbarBrand class="me-0">
          <img
            class="img-fluid rounded"
            :src="require('/assets/images/TimeofJustice.svg')"
            style="
              width: 2.3rem;
              min-width: 2.3rem;
              height: 2.3rem;
              min-height: 2.3rem;
            "
            alt="Time of Justice Logo"
          />
        </BNavbarBrand>
      </div>

      <BNavbarNav
        class="d-none d-lg-flex justify-content-between align-items-center w-100"
      >
        <div class="d-flex align-items-center ps-0 pt-0">
          <NavLinks />
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
          <font-awesome-icon icon="fa-solid fa-times" />
        </template>

        <BNavbarNav>
          <NavLinks />
        </BNavbarNav>
      </BOffcanvas>
    </div>
  </div>
</template>

<style lang="scss">
.pulse {
  animation: pulse 2s infinite;
  padding: 0.3rem !important;

  transition:
    --padding 0.2s ease-in-out,
    opacity 0.2s ease-in-out;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}

.navbar-body {
  margin: 0;
  border-radius: 0.5rem;
  transition:
    backdrop-filter 0.3s ease-in-out,
    background 0.3s ease-in-out,
    box-shadow 0.3s ease-in-out,
    padding 0.3s ease-in-out,
    margin 0.3s ease-in-out;

  @media (min-width: 1400px) {
    transition:
      width 0.8s cubic-bezier(0.68, -0.55, 0.27, 1.55),
      backdrop-filter 0.3s ease-in-out,
      background 0.3s ease-in-out,
      box-shadow 0.3s ease-in-out,
      padding 0.3s ease-in-out,
      margin 0.3s ease-in-out;

    .link-title {
      transition: max-width 0.3s ease-in-out;
      max-width: 10rem;
      overflow: hidden;
      transition-delay: 0.2s;
    }
  }
}

.navbar-body.scrolled {
  padding-left: var(--bs-navbar-brand-padding-y);
  padding-right: var(--bs-navbar-brand-padding-y);
  margin-left: calc(
    var(--bs-gutter-x) * 0.5 - var(--bs-navbar-brand-padding-y)
  );
  margin-right: calc(
    var(--bs-gutter-x) * 0.5 - var(--bs-navbar-brand-padding-y)
  );

  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 26rem;

  @media (max-width: 1400px) {
    width: 100%;
  }

  @media (min-width: 1400px) {
    .link-title {
      max-width: 0;
      transition-delay: 0s;
    }
  }
}

.offcanvas .offcanvas-header,
.offcanvas .offcanvas-body {
  --bs-gutter-x: 1.5rem;

  --bs-offcanvas-padding-y: calc(var(--bs-gutter-x) * 0.5);
  --bs-offcanvas-padding-x: calc(var(--bs-gutter-x) * 0.5);

  padding-right: 1rem;
}
</style>
