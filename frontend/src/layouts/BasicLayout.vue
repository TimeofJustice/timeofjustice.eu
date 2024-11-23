<script setup lang="ts">
import { Link, Head } from '@inertiajs/vue3'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {faBars, faHome, faPaintBrush} from "@fortawesome/free-solid-svg-icons";
import {ref} from "vue";
import LocaleDropdown from "@components/LocaleDropdown.vue";

interface IBasicLayout {
  isProduction: boolean;
}

defineProps<IBasicLayout>();

const open = ref(false);
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

    <div class="navbar navbar-expand-lg position-sticky top-0 z-1">
      <div class="container">
        <button class="navbar-toggler border-0 text-white" type="button" data-toggle="collapse" @click="open = !open">
          <FontAwesomeIcon class="navbar-toggler-icon" :icon="faBars"/>
        </button>

        <div class="navbar-brand d-flex">
          <LocaleDropdown class="d-block d-lg-none"/>

          <img class="img-fluid rounded" :src="require('/assets/images/TimeofJustice.svg')" style="width: 2.3rem;">
        </div>

        <div class="collapse navbar-collapse d-flex justify-content-between" :class="{show: open}">
          <div class="d-flex flex-column flex-lg-row gap-3 align-items-lg-center ps-3 ps-lg-0 pt-2 pt-lg-0">
            <Link class="nav-item nav-link p-0" href="/" :class="{ 'active': $page.component === 'Index' }">
              <FontAwesomeIcon :icon="faHome"/>
              <span class="ms-1">{{ $t('nav.projects') }}</span>
            </Link>
            <a class="nav-item nav-link p-0" href="https://legacy.timeofjustice.eu/place">
              <FontAwesomeIcon :icon="faPaintBrush"/>
              <span class="ms-1">{{ $t('nav.place') }}</span>
            </a>
            <BNavItemDropdown class="nav-link" :v-wip="isProduction">
              <template #button-content>
                <span>{{ $t('nav.actions') }}</span>
              </template>
              <BDropdownItem>First Action</BDropdownItem>
              <BDropdownItem>Second Action</BDropdownItem>
              <BDropdownItem>Third Action</BDropdownItem>
              <BDropdownDivider />
              <BDropdownItem active>Active action</BDropdownItem>
              <BDropdownItem disabled>Disabled action</BDropdownItem>
            </BNavItemDropdown>
          </div>

          <LocaleDropdown class="d-none d-lg-block"/>
        </div>
      </div>
    </div>

    <div class="w-100 p-4 overflow-y-auto overflow-x-hidden z-0">
      <div class="container">
        <BAlert variant="info" :model-value="true">
          <vue-markdown :source="$t('index.wip_alert')" :options="{
            linkify: true
          }" />
        </BAlert>
      </div>
      <slot></slot>
    </div>
  </div>
</template>