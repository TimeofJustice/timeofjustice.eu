<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faCode, faHouse } from "@fortawesome/free-solid-svg-icons";
import { faDiscord, faGithub, faInstagram, faLinkedin, faTwitter } from "@fortawesome/free-brands-svg-icons";
</script>

<template>
  <header class="d-flex justify-content-center p-0">
    <div class="container-xxl pt-3 nav-container">
      <nav class="nav m-0 text-white p-0 d-flex align-items-center justify-content-between">
        <section class="d-flex flex-row gap-2 justify-center align-items-center">
          <FontAwesomeIcon :icon="faCode"/>
          <span class="seperator-end">TimeofJustice</span>

          <RouterLink to="/projects">/Projects</RouterLink>
          <RouterLink to="/">/Place</RouterLink>
        </section>

        <section class="d-flex flex-row gap-2 justify-center align-items-center fs-5">
          <a><FontAwesomeIcon :icon="faGithub"/></a>
          <a><FontAwesomeIcon :icon="faInstagram"/></a>
          <a><FontAwesomeIcon :icon="faLinkedin"/></a>
          <a><FontAwesomeIcon :icon="faTwitter"/></a>
        </section>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>

</style>
