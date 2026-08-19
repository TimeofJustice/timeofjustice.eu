<script setup lang="ts">
import { Head } from "@inertiajs/vue3";

interface EntryPageProps {
  statusCode: number;
}

defineProps<EntryPageProps>();
</script>

<template>
  <Head :title="$t('games.title')" />

  <div class="container-fixed flex flex-col items-center justify-center">
    <UiAlert variant="danger">
      <vue-markdown :source="$t('games.entry.warning')" />
    </UiAlert>

    <div class="w-full shrink-0 sm:w-1/2 md:w-5/12 lg:w-1/3 xl:w-1/4">
      <UiCard body-class="flex flex-col items-center">
        <template #header>
          <h1 class="text-center m-0">
            <iconify-icon icon="fa7-solid:dice" />
            {{ $t("games.entry.title") }}
          </h1>
        </template>

        <div class="flex flex-col items-center gap-2">
          <UiButton variant="primary" class="w-full" to="/games/register/">
            {{ $t("games.entry.enter_with_new_wallet") }}
          </UiButton>
          <UiLink class="w-full" to="/games/login/">
            {{ $t("games.entry.enter_with_existing_wallet") }}
          </UiLink>
        </div>
      </UiCard>
    </div>
  </div>
</template>
