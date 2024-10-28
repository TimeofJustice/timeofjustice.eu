<script setup lang="ts">
import BasicLayout from "../layout/BasicLayout.vue";
import {Head} from '@inertiajs/vue3';
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome';
import {faGithub, faInstagram, faLinkedin, faTwitter} from "@fortawesome/free-brands-svg-icons";
</script>

<template>
  <Head title="Home"/>

  <BasicLayout>
    <div class="d-flex min-vh-100 container gap-4">
      <div class="col-md-4 d-flex flex-grow-1 justify-content-end align-items-start" style="padding-top: 10rem">
        <div class="card bg-grey-100 text-white position-sticky bg-opacity-75" style="top: 1rem;">
          <div class="card-header">
            <h5 class="mb-0">TimeofJustice</h5>
            <small class="text-grey-10">
              Jonas Oelschner
            </small>
            <i class="fi fi-de" :title="$t('index.profile.based_in')"></i>
          </div>

          <div class="card-body d-flex flex-column align-items-center gap-3" style="max-width: 18rem">
            <img class="img-fluid rounded" :src="require('@assets/images/TimeofJustice.jpg')">
            <h5 class="fw-bold text-center mb-0">
              {{ $t('index.profile.current_position') }}
            </h5>
            <div class="d-flex gap-2">
              <a class="link">
                <h4 class="mb-0"><FontAwesomeIcon :icon="faGithub"/></h4>
              </a>
              <a class="link">
                <h4 class="mb-0"><FontAwesomeIcon :icon="faInstagram"/></h4>
              </a>
              <a class="link">
                <h4 class="mb-0"><FontAwesomeIcon :icon="faLinkedin"/></h4>
              </a>
              <a class="link">
                <h4 class="mb-0"><FontAwesomeIcon :icon="faTwitter"/></h4>
              </a>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex flex-column p-2 h-100 w-100 gap-2">
        <BAlert variant="info" :model-value="true">
          {{ $t('index.wip_alert') }}
        </BAlert>

        <div class="card bg-grey-100 text-white" v-motion-slide-visible-once-right v-for:let="i in 100" :key="i">
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