<script setup lang="ts">
import { onMounted, ref, useTemplateRef, watch } from "vue";
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

/**
 * The avatar images are small, but they are still a request: in the leaderboard
 * and the picker there are a dozen of them at once, and an unpainted `<img>` is
 * a hole in an otherwise finished row.
 */
const loaded = ref(false);
const image = useTemplateRef<HTMLImageElement>("image");

const settle = () => {
  loaded.value = true;
};

onMounted(() => {
  // A cached image can beat Vue to binding `@load`; `complete` catches that.
  if (image.value?.complete) settle();
});

// The same element is reused when the wallet picks a new face, and the previous
// image having loaded says nothing about the new one.
watch(
  () => avatar?.image,
  () => {
    loaded.value = false;
  },
);
</script>

<template>
  <div
    class="flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-card text-light"
    :class="[SIZES[size], avatar && !loaded && 'skeleton']"
  >
    <!-- A plain <img> keeps animated GIFs playing; v-lazy-image swaps sources.
         The shimmer is on the circle behind it rather than on the image, which
         fades out of its own background along with everything else. -->
    <img
      ref="image"
      v-if="avatar"
      :src="avatar.image"
      :alt="avatar.name"
      class="size-full object-cover transition-opacity duration-300"
      :class="loaded ? 'opacity-100' : 'opacity-0'"
      @load="settle"
      @error="settle"
    />
    <iconify-icon v-else icon="fa6-solid:user" />
  </div>
</template>
