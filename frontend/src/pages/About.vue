<script setup lang="ts">
import BasicLayout from "../layout/BasicLayout.vue";
import { Head } from '@inertiajs/vue3';
</script>

<template>
  <Head title="About"/>

  <BasicLayout>
    <div class="d-flex min-vh-100 container gap-4">
      <div class="col-md-4 bg-white d-flex flex-grow-1 justify-content-end align-items-start pt-5">
        <div class="card bg-grey-100 text-white position-sticky" style="top: 5rem;">
          <div class="card-body">
            <img class="img-fluid" src="/assets/images/TimeofJustice.jpg">
            <h2>TimeofJustice</h2>
            <p class="fst-italic text-white">Also known as Jonas Oelschner</p>
            <p>Software Developer</p>
          </div>
        </div>
      </div>
      <div class="d-flex flex-column p-2 bg-black h-100 w-100 gap-2">
        <div class="card" v-motion-slide-visible-once-right v-for:let="i in 100" :key="i">
          <div class="card-header">Card</div>
          <div class="card-body">
            <div class="btn btn-primary">Button</div>
          </div>
        </div>
      </div>
    </div>
  </BasicLayout>
</template>

<style scoped lang="scss">

</style>