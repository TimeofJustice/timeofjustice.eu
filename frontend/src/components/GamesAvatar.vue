<script setup lang="ts">
import { Avatar } from "@/types/Avatar.ts";

interface GamesAvatarProps {
  avatar: Avatar | null;
  size?: "sm" | "md" | "lg";
}

const { avatar, size = "md" } = defineProps<GamesAvatarProps>();

const SIZES = {
  sm: "size-6 text-[0.7rem]",
  md: "size-9 text-base",
  lg: "size-full text-2xl",
};
</script>

<template>
  <div
    class="flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-card text-light"
    :class="SIZES[size]"
  >
    <!-- A plain <img> keeps animated GIFs playing; v-lazy-image swaps sources. -->
    <img
      v-if="avatar"
      :src="avatar.image"
      :alt="avatar.name"
      class="size-full object-cover"
    />
    <iconify-icon v-else icon="fa6-solid:user" />
  </div>
</template>
