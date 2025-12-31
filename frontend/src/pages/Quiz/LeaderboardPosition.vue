<script setup lang="ts">
interface LeaderboardPositionProps {
  name: string;
}

const props = defineProps<LeaderboardPositionProps>();
</script>

<template>
  <div class="item">
    <BCard body-class="p-2 d-flex align-items-center gap-2" class="w-100">
      <BAvatar class="p-0 border border-2 border-black">
        <span class="b-avatar-img position-absolute">
          <img
            src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif"
          />
        </span>
      </BAvatar>
      {{ props.name }}
    </BCard>
  </div>
</template>

<style scoped lang="scss"></style>
