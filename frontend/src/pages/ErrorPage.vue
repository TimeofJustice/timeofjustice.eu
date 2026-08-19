<script setup lang="ts">
import { Head } from "@inertiajs/vue3";

interface ErrorPageProps {
  statusCode: number;
}

defineProps<ErrorPageProps>();

const errorMessages: Record<number, string> = {
  400: "error.bad_request",
  403: "error.permission_denied",
  404: "error.page_not_found",
  500: "error.server_error",
};
</script>

<template>
  <Head :title="$t('general.error')" />

  <div class="container-fixed flex flex-col items-center pt-12">
    <div class="relative flex flex-col items-center">
      <div class="text-fade absolute text-center leading-none font-medium">
        {{ statusCode }}
      </div>

      <div class="z-3 flex flex-col items-center justify-center text-h5">
        <div class="text-center text-h1-fluid font-bold xl:text-h1">
          {{ $t(errorMessages[statusCode] || "error.unknown_error") }}
        </div>
        <div class="text-center lg:w-7/12">
          {{ $t("error.message") }}
        </div>
        <UiLink variant="light" to="/">
          <iconify-icon icon="fa6-solid:house" />
          {{ $t("error.back") }}
        </UiLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-fade {
  -webkit-background-clip: text;
  background-clip: text;

  background-image: linear-gradient(
    transparent,
    color-mix(in srgb, var(--color-light) 65%, transparent)
  );
  color: transparent;

  font-size: 25rem;
}

@media (max-width: 768px) {
  .text-fade {
    font-size: 15rem;
  }
}

@media (max-width: 576px) {
  .text-fade {
    font-size: 10rem;
  }
}
</style>
