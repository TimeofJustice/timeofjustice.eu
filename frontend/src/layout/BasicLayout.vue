<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {faBars, faHome, faPaintBrush} from "@fortawesome/free-solid-svg-icons";
import {ref} from "vue";

const open = ref(false);
</script>

<template>
  <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column">
    <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex justify-content-center align-items-center bg-space-blue">
      <div class="gradient"></div>
    </div>

    <div class="navbar navbar-expand-lg position-sticky top-0">
      <div class="container">
        <button class="navbar-toggler border-0" type="button" data-toggle="collapse" @click="open = !open">
          <FontAwesomeIcon class="navbar-toggler-icon" :icon="faBars"/>
        </button>

        <div class="navbar-brand">
          <img class="img-fluid rounded" src="/assets/images/TimeofJustice.jpg" style="width: 2rem;">
        </div>

        <div class="collapse navbar-collapse" :class="{show: open}">
          <div class="d-flex flex-column flex-lg-row gap-3 align-items-lg-center ps-3 ps-lg-0 pt-2 pt-lg-0">
            <Link class="nav-item nav-link p-0" href="/"><FontAwesomeIcon :icon="faHome"/> Projects</Link>
            <Link class="nav-item nav-link p-0" href="/about"><FontAwesomeIcon :icon="faPaintBrush"/> r/Place</Link>
          </div>
        </div>
      </div>
    </div>

    <div class="w-100 p-4 overflow-y-auto overflow-x-hidden">
      <slot></slot>
    </div>
  </div>
</template>