<script setup lang="ts">
import { faBars, faClose, faDice, faHome, faPaintBrush } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@node_modules/@fortawesome/vue-fontawesome";
import LocaleDropdown from "@components/LocaleDropdown.vue";
import { onMounted, ref } from "vue";

interface IBasicLayout {
  navbar: 'small' | 'large';
}

defineProps<IBasicLayout>();

// Check if the page is scrolled to add a shadow to the navbar
const isScrolled = ref(false);
onMounted(() => {
  window.addEventListener('scroll', () => {
    isScrolled.value = window.scrollY > 0;
  });
});
</script>

<template>
  <div class="navbar navbar-expand-lg position-sticky top-0 z-1 w-100 d-flex align-content-center justify-content-center px-2">
    <div class="container-xxl navbar-body px-1" :class="{ 'scrolled': isScrolled || navbar === 'small' }">
      <BButton variant="tertiary" class="btn-square navbar-toggler border-0 text-white" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar">
        <FontAwesomeIcon :icon="faBars"/>
      </BButton>

      <div class="navbar-brand d-flex me-0 me-lg-3">
        <LocaleDropdown class="d-block d-lg-none"/>

        <img class="img-fluid rounded" :src="require('/assets/images/TimeofJustice.svg')" style="width: 2.3rem; height: 2.3rem;" alt="Time of Justice Logo"/>
      </div>

      <div class="navbar-nav offcanvas offcanvas-start offcanvas-small d-flex justify-content-between flex-lg-row" id="offcanvasNavbar">
        <div class="offcanvas-header">
          <BButton variant="tertiary" class="btn-square ms-0" type="button" data-bs-dismiss="offcanvas">
            <font-awesome-icon :icon="faClose"/>
          </BButton>
        </div>

        <div class="offcanvas-body d-flex flex-column flex-lg-row align-items-lg-center ps-3 ps-lg-0 pt-2 pt-lg-0">
          <BLink class="nav-item nav-link p-0 px-2" to="/" :class="{ 'active': $page.component === 'Projects' }">
            <FontAwesomeIcon :icon="faHome"/>
            <span class="ms-1">{{ $t('nav.projects') }}</span>
          </BLink>
          <BLink class="nav-item nav-link p-0 px-2" to="/games/" :class="{ 'active': $page.component === 'Games/Main' }">
            <FontAwesomeIcon :icon="faDice"/>
            <span class="ms-1">{{ $t('nav.games') }}</span>
          </BLink>
          <BLink class="nav-item nav-link p-0 px-2 position-relative" to="/r-place/" :class="{ 'active': $page.component === 'RPlace' }">
            <FontAwesomeIcon :icon="faPaintBrush"/>
            <span class="ms-1">{{ $t('nav.place') }}</span>
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
  border-radius: 0.5rem;
  transition: width 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55), backdrop-filter 0.3s ease-in-out, background 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

.navbar-body.scrolled {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 45rem;

  background: rgba(37, 37, 37, 0.4);
  backdrop-filter: brightness(1.1) blur(10px);
  -webkit-backdrop-filter: brightness(1.1) blur(10px);

  -webkit-box-shadow: inset 0 2px 0 -2px rgba(118, 118, 118, 0.7),
  inset 0 0 5px 1px rgba(118, 118, 118, 0.3);
  box-shadow: inset 0 2px 0 -2px rgba(118, 118, 118, 0.7),
  inset 0 0 5px 1px rgba(118, 118, 118, 0.3);
}

.navbar-body.scrolled > .navbar-nav {

}
</style>