<script setup lang="ts">
import { faBars, faClose, faDice, faHome, faPaintBrush } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@node_modules/@fortawesome/vue-fontawesome";
import LocaleDropdown from "@components/LocaleDropdown.vue";
import { onMounted, ref } from "vue";

interface IBasicLayout {
  small?: boolean;
}

defineProps<IBasicLayout>();

// Check if the page is scrolled to add a shadow to the navbar
const isScrolled = ref(false);
onMounted(() => {
  const parent: HTMLElement = document.querySelector('.content-body')!;
  parent.addEventListener('scroll', () => {
    isScrolled.value = parent.scrollTop > 0;
  });
});
</script>

<template>
  <div class="navbar navbar-expand-lg top-0 z-1 w-100 d-flex align-content-center justify-content-center pe-none" :class="{ 'position-absolute': small, 'position-sticky': !small }">
    <div class="container-xxl navbar-body pe-auto" :class="{ 'scrolled blur-box': isScrolled || small}">
      <BButton variant="tertiary" class="btn-square navbar-toggler border-0 text-white" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar">
        <FontAwesomeIcon :icon="faBars"/>
      </BButton>

      <div class="navbar-brand d-flex me-0 me-lg-3">
        <LocaleDropdown class="d-block d-lg-none"/>

        <img class="img-fluid rounded" :src="require('/assets/images/TimeofJustice.svg')" style="width: 2.3rem; min-width: 2.3rem; height: 2.3rem; min-height: 2.3rem;" alt="Time of Justice Logo"/>
      </div>

      <div class="navbar-nav offcanvas offcanvas-start offcanvas-small d-flex justify-content-between flex-lg-row" id="offcanvasNavbar">
        <div class="offcanvas-header">
          <BButton variant="tertiary" class="btn-square ms-0" type="button" data-bs-dismiss="offcanvas">
            <font-awesome-icon :icon="faClose"/>
          </BButton>
        </div>

        <div class="offcanvas-body d-flex flex-column flex-lg-row align-items-lg-center ps-3 ps-lg-0 pt-2 pt-lg-0">
          <BLink class="nav-item nav-link p-0 px-2 d-flex align-items-center" to="/" :class="{ 'active': $page.component === 'Projects' }">
            <FontAwesomeIcon :icon="faHome"/>
            <div class="ms-1 link-title">{{ $t('nav.projects') }}</div>
          </BLink>
          <BLink class="nav-item nav-link p-0 px-2 d-flex align-items-center" to="/games/" :class="{ 'active': $page.component === 'Games/Main' || $page.component === 'Games/Entry' || $page.component === 'Games/Login' }">
            <FontAwesomeIcon :icon="faDice"/>
            <div class="ms-1 link-title">{{ $t('nav.games') }}</div>
          </BLink>
          <BLink class="nav-item nav-link p-0 px-2 position-relative d-flex align-items-center" to="/r-place/" :class="{ 'active': $page.component === 'RPlace' }">
            <FontAwesomeIcon :icon="faPaintBrush"/>
            <div class="ms-1 link-title">{{ $t('nav.place') }}</div>
            <BBadge
              variant="danger"
              class="position-absolute top-0 start-100 translate-middle mt-1 me-1 border-0 pulse"
              dot-indicator
            >
            </BBadge>
          </BLink>
        </div>

        <LocaleDropdown class="d-none d-lg-block"/>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.pulse {
  animation: pulse 2s infinite;
  padding: 0.3rem!important;

  transition: --padding 0.2s ease-in-out, opacity 0.2s ease-in-out;
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
  transition: backdrop-filter 0.3s ease-in-out, background 0.3s ease-in-out, box-shadow 0.3s ease-in-out, padding 0.3s ease-in-out, margin 0.3s ease-in-out;

  @media (min-width: 1400px) {
    transition: width 0.8s cubic-bezier(0.68, -0.55, 0.27, 1.55), backdrop-filter 0.3s ease-in-out, background 0.3s ease-in-out, box-shadow 0.3s ease-in-out, padding 0.3s ease-in-out, margin 0.3s ease-in-out;
  }
}

.navbar-body.scrolled {
  padding-left: var(--bs-navbar-brand-padding-y);
  padding-right: var(--bs-navbar-brand-padding-y);
  margin-left: calc(var(--bs-gutter-x) * 0.5 - var(--bs-navbar-brand-padding-y));
  margin-right: calc(var(--bs-gutter-x) * 0.5 - var(--bs-navbar-brand-padding-y));

  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 26rem;

  @media (max-width: 1400px) {
    width: 100%;
  }
}

@media (min-width: 1400px) {
  .navbar-body .link-title {
    transition: max-width 0.3s ease-in-out;
    max-width: 10rem;
    overflow: hidden;
    transition-delay: 0.2s;
  }

  .navbar-body.scrolled .link-title {
    max-width: 0;
    transition-delay: 0s;
  }
}
</style>