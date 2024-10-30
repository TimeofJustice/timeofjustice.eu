<script setup lang="ts">
import Social from "@types/Social.vue";

interface Props {
  socials: Social[];
  variant?: 'small' | 'large';
}

withDefaults(defineProps<Props>(), {
  variant: 'large',
});
</script>

<template>
  <div class="card bg-grey-100 text-white bg-opacity-75" v-if="variant === 'large'">
    <div class="card-header">
      <h5 class="mb-0">TimeofJustice</h5>
      <small class="text-grey-10">
        Jonas Oelschner
      </small>
      <i class="fi fi-de" :title="$t('index.profile.based_in')"></i>
    </div>

    <div class="card-body d-flex flex-column align-items-center gap-3" style="max-width: 18rem">
      <img class="img-fluid rounded" :src="require('@assets/images/TimeofJustice.jpg')" alt="TimeofJustice">
      <h5 class="fw-bold text-center mb-0">
        {{ $t("index.profile.current_position") }}
      </h5>
      <div class="d-flex gap-2">
        <a
          class="link"
          :title="$t(`socials.${social.type}`)"
          :href="social.url"
          target="_blank"
          v-for="social in socials" :key="social.type"
        >
          <h4 class="mb-0">
            <font-awesome-icon :icon="social.icon" />
          </h4>
        </a>
      </div>
    </div>
  </div>

  <div class="card bg-grey-100 text-white bg-opacity-75" v-else>
    <div class="row g-0">
      <div class="col-4 ps-3 pt-3 pb-3">
        <img class="img-fluid rounded" :src="require('@assets/images/TimeofJustice.jpg')" alt="TimeofJustice">
      </div>
      <div class="col-8">
        <div class="card-body d-flex flex-column gap-2 h-100">
          <div>
            <h5 class="card-title mb-0">TimeofJustice</h5>
            <div>
              <small class="text-grey-10">
                Jonas Oelschner
              </small>
              <i class="fi fi-de" :title="$t('index.profile.based_in')"></i>
            </div>
          </div>

          {{ $t("index.profile.current_position") }}

          <div class="d-flex gap-2">
            <a
              class="link"
              :title="$t(`socials.${social.type}`)"
              :href="social.url"
              target="_blank"
              v-for="social in socials" :key="social.type"
            >
              <h4 class="mb-0">
                <font-awesome-icon :icon="social.icon" />
              </h4>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>