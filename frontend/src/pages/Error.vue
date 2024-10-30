<script setup lang="ts">
import { Link, Head } from '@inertiajs/vue3'

interface Props {
  status_code: number;
}

defineProps<Props>();
</script>

<template>
  <Head :title="$t('general.error')" />

  <div class="container d-flex flex-column align-items-center">
    <div class="text-white text-center fw-bold" style="font-size: 12rem">
      <div class="text-grey-100" style="letter-spacing: 2rem">{{status_code}}</div>
      <div style="text-transform: uppercase; font-size: 5rem">{{ $t('general.error') }}</div>
    </div>

    <Link class="btn btn-primary mt-4" href="/">
      <font-awesome-icon icon="arrow-left"/>
      {{ $t('general.back') }}
    </Link>
  </div>
</template>