<script setup lang="ts">
import BasicLayout from "../layout/BasicLayout.vue";
import { Head } from '@inertiajs/vue3'
</script>

<template>
  <Head title="Home"/>

  <BasicLayout>
    <div class="d-flex min-vh-100">
      <div class="bg-white h-100 p-5">
        <div class="card">
          <div class="card-header">Card</div>
          <div class="card-body">
            <div class="btn btn-primary" v-motion-slide-visible-once-left>Button</div>
          </div>
        </div>
      </div>
      <div class="d-flex flex-column p-2 bg-black h-100 w-100 gap-2">
        <div class="card" v-motion-slide-visible-once-right v-for:let="i in 10" :key="i">
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