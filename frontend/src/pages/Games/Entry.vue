<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { faDice } from "@node_modules/@fortawesome/free-solid-svg-icons";

interface Props {
  status_code: number;
}

defineProps<Props>();
</script>

<template>
  <Head :title="$t('games.title')" />

  <div
    class="container text-white d-flex flex-column align-items-center justify-content-center"
  >
    <BAlert :model-value="true" variant="danger">
      <vue-markdown :source="$t('games.entry.warning')" />
    </BAlert>

    <div class="col-12 col-sm-6 col-md-5 col-lg-4 col-xl-3">
      <BCard
        class="blur-box border-0"
        body-class="d-flex flex-column align-items-center"
      >
        <template #header>
          <h1 class="text-center">
            <font-awesome-icon :icon="faDice" />
            {{ $t("games.entry.title") }}
          </h1>
        </template>

        <div class="d-flex flex-column align-items-center gap-2">
          <BButton variant="primary" class="w-100" to="/games/register/">
            {{ $t("games.entry.enter_with_new_wallet") }}
          </BButton>
          <BButton variant="secondary" class="w-100" to="/games/login/">
            {{ $t("games.entry.enter_with_existing_wallet") }}
          </BButton>
        </div>
      </BCard>
    </div>
  </div>
</template>
