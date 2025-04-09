<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import Navbar from "@layouts/components/Navbar.vue";

interface IBasicLayout {
  production: boolean;
  stable: boolean;
}

defineProps<IBasicLayout>();
</script>

<template>
  <Head>
    <link rel="icon" :href="require('@assets/images/favicon.png')" />
  </Head>

  <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column overflow-hidden">
    <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex justify-content-center align-items-center bg-space-blue">
      <div class="gradient"></div>
      <div class="x-wing" v-for="i in 5" :key="i" v-if="$i18n.locale === 'yoda'">
        <i class="fi fi-x-wing"></i>
      </div>
    </div>

    <Navbar />

    <div class="w-100 overflow-y-auto overflow-x-hidden z-0">
      <div class="container-xxl px-3" v-if="!stable">
        <BAlert :model-value="true" variant="info">
          <vue-markdown :source="$t('nav.stable_hint')" />
        </BAlert>
      </div>

      <slot></slot>
    </div>
  </div>
</template>