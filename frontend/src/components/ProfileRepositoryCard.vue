<script setup lang="ts">
interface ProfileRepositoryCard {
  repository: string;
}

defineProps<ProfileRepositoryCard>();
</script>

<template>
  <UiCard
    class="overflow-hidden"
    body-class="flex flex-col gap-4"
    v-if="repository"
  >
    <h5 class="mb-0">{{ $t("profile.repository.title") }}</h5>

    <img
      class="h-auto max-w-full"
      :src="repository"
      :alt="$t('profile.repository.alt')"
    />
  </UiCard>
</template>
