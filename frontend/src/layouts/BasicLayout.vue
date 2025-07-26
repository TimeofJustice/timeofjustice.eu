<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import Navbar from "@layouts/components/Navbar.vue";
import { faClose } from "@node_modules/@fortawesome/free-solid-svg-icons";

interface IBasicLayout {
  production: boolean;
  stable: boolean;
  smallNavbar?: boolean;
}

defineProps<IBasicLayout>();
</script>

<template>
  <Head>
    <link
      rel="icon"
      type="image/png"
      href="/files/global/favicon/favicon-96x96.png"
      sizes="96x96"
    />
    <link
      rel="icon"
      type="image/svg+xml"
      href="/files/global/favicon/favicon.svg"
    />
    <link rel="shortcut icon" href="/files/global/favicon/favicon.ico" />
    <link
      rel="apple-touch-icon"
      sizes="180x180"
      href="/files/global/favicon/apple-touch-icon.png"
    />
    <meta name="apple-mobile-web-app-title" content="timeofjustice.eu" />
    <link rel="manifest" href="/files/global/favicon/site.webmanifest" />
  </Head>

  <div
    class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column overflow-hidden"
  >
    <div
      class="position-absolute top-0 bottom-0 start-0 end-0 d-flex justify-content-center align-items-center bg-space-blue vw-100 vh-100"
    >
      <div class="gradient"></div>
      <div
        class="x-wing"
        v-for="i in 5"
        :key="i"
        v-if="$i18n.locale === 'yoda'"
      >
        <i class="fi fi-x-wing"></i>
      </div>
    </div>

    <div
      class="content-body w-100 z-0 flex-grow-1 d-flex flex-column overflow-y-auto overflow-x-hidden position-relative"
    >
      <Navbar :small="smallNavbar" />

      <slot></slot>

      <div
        class="container position-fixed bottom-0 start-0 end-0 z-3"
        v-if="!stable"
      >
        <BAlert
          :model-value="true"
          variant="info"
          dismissible
          close-variant="tertiary"
        >
          <template #close>
            <font-awesome-icon :icon="faClose" />
          </template>

          <vue-markdown :source="$t('nav.stable_hint')" />
        </BAlert>
      </div>
    </div>
  </div>
</template>
