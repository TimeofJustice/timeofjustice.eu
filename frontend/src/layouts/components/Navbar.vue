<script setup lang="ts">
import { faBars, faClose, faHome, faPaintBrush } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@node_modules/@fortawesome/vue-fontawesome";
import LocaleDropdown from "@components/LocaleDropdown.vue";
import { Link } from "@node_modules/@inertiajs/vue3";
</script>

<template>
  <div class="navbar navbar-expand-lg position-sticky top-0 z-1">
    <div class="container-xxl">
      <button class="navbar-toggler border-0 text-white" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar">
        <FontAwesomeIcon class="navbar-toggler-icon" :icon="faBars"/>
      </button>

      <div class="navbar-brand d-flex me-0 me-lg-3">
        <LocaleDropdown class="d-block d-lg-none"/>

        <img class="img-fluid rounded" :src="require('/assets/images/TimeofJustice.svg')" style="width: 2.3rem;">
      </div>

      <div class="navbar-nav offcanvas offcanvas-start offcanvas-small d-flex justify-content-between flex-lg-row" id="offcanvasNavbar">
        <div class="offcanvas-header">
          <button class="btn-close ms-0" type="button" data-bs-dismiss="offcanvas">
            <font-awesome-icon :icon="faClose"/>
          </button>
        </div>

        <div class="offcanvas-body d-flex flex-column flex-lg-row gap-3 align-items-lg-center ps-3 ps-lg-0 pt-2 pt-lg-0">
          <Link class="nav-item nav-link p-0" href="/" :class="{ 'active': $page.component === 'Projects' }">
            <FontAwesomeIcon :icon="faHome"/>
            <span class="ms-1">{{ $t('nav.projects') }}</span>
          </Link>
          <a class="nav-item nav-link p-0" href="https://legacy.timeofjustice.eu/place">
            <FontAwesomeIcon :icon="faPaintBrush"/>
            <span class="ms-1">{{ $t('nav.place') }}</span>
          </a>
        </div>

        <LocaleDropdown class="d-none d-lg-block"/>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>