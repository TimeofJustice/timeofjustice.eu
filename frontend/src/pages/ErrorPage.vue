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

  <div class="container d-flex flex-column align-items-center pt-5">
    <div class="position-relative d-flex flex-column align-items-center">
      <div class="fw-medium lh-1 text-fade position-absolute text-center">
        {{ statusCode }}
      </div>

      <div
        class="d-flex flex-column align-items-center justify-content-center z-3 fs-5"
      >
        <div class="text-center fs-1 fw-bold">
          {{ $t(errorMessages[statusCode] || "error.unknown_error") }}
        </div>
        <div class="text-center col-lg-7">
          {{ $t("error.message") }}
        </div>
        <BLink variant="light" to="/">
          <iconify-icon icon="fa6-solid:house" />
          {{ $t("error.back") }}
        </BLink>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.text-fade {
  -webkit-background-clip: text;
  background-clip: text;

  background-image: linear-gradient(
    transparent,
    color-mix(in srgb, var(--bs-light) 65%, transparent)
  );
  color: transparent;

  font-size: 25rem;

  @media (max-width: 768px) {
    font-size: 15rem;
  }

  @media (max-width: 576px) {
    font-size: 10rem;
  }
}
</style>
