<script setup lang="ts">
interface Props {
  status_code: number;
}

defineProps<Props>();
</script>

<template>
  <div class="container text-white text-center">
    <h1>Error {{status_code}}</h1>
  </div>
</template>

<style scoped lang="scss">

</style>