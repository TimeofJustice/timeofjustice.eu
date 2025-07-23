<script setup lang="ts">
import { faDice, faHome, faPaintBrush } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@node_modules/@fortawesome/vue-fontawesome";
</script>

<template>
  <BNavItem to="/" link-class="d-flex align-items-center" :class="{ 'active': $page.component === 'Projects' }">
    <FontAwesomeIcon :icon="faHome"/>
    <div class="ms-1 link-title">{{ $t('nav.projects') }}</div>
  </BNavItem>
  <BNavItem to="/games/" link-class="d-flex align-items-center" :class="{ 'active': $page.component === 'Games/Main' || $page.component === 'Games/Entry' || $page.component === 'Games/Login' }">
    <FontAwesomeIcon :icon="faDice"/>
    <div class="ms-1 link-title">{{ $t('nav.games') }}</div>
  </BNavItem>
  <BNavItem to="/r-place/" link-class="d-flex align-items-center position-relative" :class="{ 'active': $page.component === 'RPlace' }">
    <FontAwesomeIcon :icon="faPaintBrush"/>
    <div class="ms-1 link-title">{{ $t('nav.place') }}</div>
    <BBadge
      variant="danger"
      class="position-absolute top-0 start-100 translate-middle mt-1 me-1 border-0 pulse"
      dot-indicator
    >
    </BBadge>
  </BNavItem>
</template>

<style scoped lang="scss">

</style>