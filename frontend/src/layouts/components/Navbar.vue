<script setup lang="ts">
import { faBars, faClose, faDice, faHome, faPaintBrush } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@node_modules/@fortawesome/vue-fontawesome";
import LocaleDropdown from "@components/LocaleDropdown.vue";
</script>

<template>
  <div class="navbar navbar-expand-lg position-sticky top-0 z-1">
    <div class="container-xxl px-3">
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
</style>