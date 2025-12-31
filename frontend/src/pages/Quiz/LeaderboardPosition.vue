<script setup lang="ts">
interface LeaderboardPositionProps {
  name: string;
  url: string;
}

const props = defineProps<LeaderboardPositionProps>();
</script>

<template>
  <div class="item">
    <BCard body-class="p-2 d-flex align-items-center gap-2" class="w-100">
      <BAvatar class="p-0 border border-2 border-black">
        <span class="b-avatar-img position-absolute">
          <img :src="url" />
        </span>
      </BAvatar>
      {{ props.name }}
    </BCard>
  </div>
</template>

<style scoped lang="scss"></style>
