<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from "vue";
import { Carousel, Slide } from "vue3-carousel";
import { ProjectImage } from "@/types/ProjectImage.ts";

interface ProjectCarouselProps {
  items: ProjectImage[];
}

const { items } = defineProps<ProjectCarouselProps>();

const currentSlide = ref(0);
const currentItem = ref<ProjectImage | null>(
  items.length > 0 ? items[0] : null,
);

const isMouseOver = ref(false);
const isFullscreenOpen = ref(false);

const fullscreenVideoPlayer = ref<HTMLVideoElement | null>(null);

const galleryConfig = {
  itemsToShow: 1,
  mouseDrag: false,
  touchDrag: false,
  height: 320,
  slideEffect: "fade" as const,
};

const stopVideoPlayer = (player: HTMLVideoElement) => {
  if (!player) return;

  player.pause();
  player.currentTime = 0;
};

const slideToIndex = (index: number) => {
  const videoPlayer = document.getElementById(
    "carousel-video-player-" + currentSlide.value,
  ) as HTMLVideoElement;
  stopVideoPlayer(videoPlayer);

  currentSlide.value = ((index % items.length) + items.length) % items.length;
  currentItem.value = items[currentSlide.value];
};

const isVideoPlaying = () => {
  const video = document.getElementById(
    "carousel-video-player-" + currentSlide.value,
  ) as HTMLVideoElement;
  return (
    video &&
    video.currentTime > 0 &&
    !video.paused &&
    !video.ended &&
    video.readyState > 2
  );
};

const slideToNextIndex = () => {
  if (!isMouseOver.value && !isVideoPlaying() && !isFullscreenOpen.value)
    slideToIndex(currentSlide.value + 1);
};

const slide = (offset: number) => {
  const nextIndex = currentSlide.value + offset;
  slideToIndex(nextIndex);

  clearInterval(autoSlideInterval);
  autoSlideInterval = setInterval(slideToNextIndex, 5000);
};

let autoSlideInterval = setInterval(slideToNextIndex, 5000);
onBeforeUnmount(() => {
  clearInterval(autoSlideInterval);
});

const openFullscreen = () => {
  isFullscreenOpen.value = true;

  const videoPlayer = document.getElementById(
    "carousel-video-player-" + currentSlide.value,
  ) as HTMLVideoElement;
  stopVideoPlayer(videoPlayer);
};

const closeFullscreen = () => {
  if (fullscreenVideoPlayer.value) stopVideoPlayer(fullscreenVideoPlayer.value);

  isFullscreenOpen.value = false;
};

watch(
  () => items,
  () => {
    currentSlide.value = 0;
    currentItem.value = items.length > 0 ? items[0] : null;
  },
);
</script>

<template>
  <div
    v-if="items.length"
    @mouseover="isMouseOver = true"
    @mouseleave="isMouseOver = false"
  >
    <Carousel v-bind="galleryConfig" v-model="currentSlide">
      <Slide v-for="(image, i) in items" :key="i">
        <v-lazy-image
          class="slide gallery"
          :src="image.image.original"
          :alt="image.alt"
          v-if="!image.video"
        />
        <div class="slide gallery" v-else>
          <video
            :src="image.video"
            autoplay
            muted
            controls
            playsinline
            :id="`carousel-video-player-` + i"
          />
        </div>

        <UiButton
          variant="primary"
          circle
          class="absolute top-0 right-0 m-2"
          @click="openFullscreen()"
        >
          <iconify-icon icon="fa6-solid:maximize" />
        </UiButton>
      </Slide>

      <div
        class="absolute bottom-0 left-0 flex w-full justify-center gap-1 p-1 text-[0.6rem]"
      >
        <iconify-icon
          :icon="
            currentSlide === i ? 'fa6-solid:circle-dot' : 'fa6-solid:circle'
          "
          class="carousel__indicator"
          @click="slideToIndex(i)"
          v-for="(_, i) in items"
          :key="i"
        />
      </div>

      <template #addons>
        <UiButton
          variant="primary"
          circle
          class="carousel__prev m-2"
          @click="slide(-1)"
        >
          <iconify-icon icon="fa6-solid:chevron-left" />
        </UiButton>
        <UiButton
          variant="primary"
          circle
          class="carousel__next m-2"
          @click="slide(+1)"
        >
          <iconify-icon icon="fa6-solid:chevron-right" />
        </UiButton>
      </template>
    </Carousel>
  </div>

  <div
    class="fullscreen fixed top-0 left-0 h-full w-full overflow-hidden"
    :class="{ open: isFullscreenOpen }"
  >
    <div
      class="fullscreen-body relative flex h-full w-full items-center justify-center overflow-hidden p-2"
      @click.self="closeFullscreen()"
    >
      <v-lazy-image
        :src="currentItem?.image.original"
        :alt="currentItem?.alt"
        v-if="!currentItem?.video && currentItem?.image.original"
      />
      <video
        :src="currentItem?.video"
        controls
        playsinline
        ref="fullscreenVideoPlayer"
        v-else
      />

      <UiButton
        variant="primary"
        circle
        class="absolute top-0 right-0 m-2"
        @click="closeFullscreen()"
      >
        <iconify-icon icon="ep:close-bold" />
      </UiButton>
    </div>
  </div>
</template>

<style scoped>
.carousel {
  z-index: 0;
}

.carousel .slide {
  width: 100%;
  height: 100%;

  border-radius: 8px;
  object-fit: cover;
}

.carousel .slide.gallery {
  width: 100%;
  height: 100%;

  border-radius: 16px;
  overflow: hidden;
}

.carousel .slide.gallery > video {
  width: 100%;
  height: 100%;

  border-radius: 16px;
  object-fit: cover;
}

.carousel .carousel__indicator {
  cursor: pointer;
}

.fullscreen {
  z-index: 9999;
  opacity: 0;
  pointer-events: none;
  background-color: rgb(0 0 0 / 0.5);

  transition: opacity 0.3s ease-in-out;
}

.fullscreen.open {
  pointer-events: auto;
  opacity: 1;
}

.fullscreen .fullscreen-body > video,
.fullscreen .fullscreen-body img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;

  transform: translateY(50%);
  transition: transform 0.3s ease-in-out;
}

.fullscreen.open .fullscreen-body > video,
.fullscreen.open .fullscreen-body img {
  transform: translateY(0);
}
</style>
