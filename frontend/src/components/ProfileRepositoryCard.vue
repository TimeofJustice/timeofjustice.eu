<script setup lang="ts">
import { onMounted, ref, useTemplateRef, watch } from "vue";

interface ProfileRepositoryCard {
  repository: string;
}

const { repository } = defineProps<ProfileRepositoryCard>();

/**
 * The card is an image rendered on someone else's server, so it lands well
 * after the page it sits on. Kept as a plain `<img>` rather than
 * `v-lazy-image`: that component swaps the source once the element scrolls
 * into view, and this one is above the fold in the sticky column anyway.
 */
const loaded = ref(false);
const image = useTemplateRef<HTMLImageElement>("image");

const settle = () => {
  loaded.value = true;
};

onMounted(() => {
  // A cached image can finish before Vue has bound `@load`, and then the event
  // never comes. `complete` is the only thing that knows either way.
  if (image.value?.complete) settle();
});

// A different repository is a different image, and the old one having loaded
// says nothing about the new one.
watch(
  () => repository,
  () => {
    loaded.value = false;
  },
);
</script>

<template>
  <UiCard
    class="overflow-hidden"
    body-class="flex flex-col gap-4"
    v-if="repository"
  >
    <h5 class="mb-0">{{ $t("profile.repository.title") }}</h5>

    <div class="relative">
      <!-- The URL is whatever the admin pointed at, so there is no ratio worth
           assuming. A fixed placeholder height reserves roughly the room a
           stats card takes; the image takes over its own height on arrival. -->
      <UiSkeleton
        variant="rect"
        class="h-32 w-full"
        aria-hidden="true"
        role="presentation"
        v-if="!loaded"
      />

      <!-- Out of flow until it has something to show, so it contributes no
           height next to the placeholder standing in for it. -->
      <img
        ref="image"
        class="h-auto max-w-full transition-opacity duration-300"
        :class="loaded ? 'opacity-100' : 'absolute inset-0 opacity-0'"
        :src="repository"
        :alt="$t('profile.repository.alt')"
        @load="settle"
        @error="settle"
      />
    </div>
  </UiCard>
</template>
