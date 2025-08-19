<script setup lang="ts">
interface ProfileRepositoryCard {
  repository: string;
}

defineProps<ProfileRepositoryCard>();
</script>

<template>
  <BCard
    class="card overflow-hidden"
    body-class="d-flex flex-column gap-3"
    v-if="repository"
  >
    <h5 class="mb-0">{{ $t("profile.repository.title") }}</h5>

    <img
      class="img-fluid"
      :src="repository"
      :alt="$t('profile.repository.alt')"
    />
  </BCard>
</template>

<style scoped lang="scss"></style>
