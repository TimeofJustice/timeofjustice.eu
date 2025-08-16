<script setup lang="ts">
import { onBeforeUnmount, ref } from "vue";
import { Carousel, Slide } from "vue3-carousel";
import { TranslatedText } from "@/types/TranslatedText.ts";
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
          :alt="image.alt[$i18n.locale as keyof TranslatedText]"
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

        <BButton
          variant="primary"
          class="btn-circle position-absolute top-0 end-0 m-2"
          @click="openFullscreen()"
        >
          <iconify-icon icon="fa6-solid:maximize" />
        </BButton>
      </Slide>

      <div
        class="position-absolute bottom-0 start-0 w-100 d-flex justify-content-center gap-1 p-1"
        style="font-size: 0.6rem"
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
        <BButton
          variant="primary"
          class="btn-circle m-2 carousel__prev"
          @click="slide(-1)"
        >
          <iconify-icon icon="fa6-solid:chevron-left" />
        </BButton>
        <BButton
          variant="primary"
          class="btn-circle m-2 carousel__next"
          @click="slide(+1)"
        >
          <iconify-icon icon="fa6-solid:chevron-right" />
        </BButton>
      </template>
    </Carousel>
  </div>

  <div
    class="position-fixed top-0 start-0 w-100 h-100 overflow-hidden fullscreen"
    :class="{ open: isFullscreenOpen }"
  >
    <div
      class="d-flex justify-content-center align-items-center position-relative p-2 w-100 h-100 overflow-hidden fullscreen-body"
      @click.self="closeFullscreen()"
    >
      <v-lazy-image
        :src="currentItem?.image.original"
        :alt="currentItem?.alt[$i18n.locale as keyof TranslatedText]"
        v-if="!currentItem?.video && currentItem?.image.original"
      />
      <video
        :src="currentItem?.video"
        controls
        playsinline
        ref="fullscreenVideoPlayer"
        v-else
      />

      <BButton
        variant="primary"
        class="btn-circle position-absolute top-0 end-0 m-2"
        @click="closeFullscreen()"
      >
        <iconify-icon icon="ep:close-bold" />
      </BButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
.carousel {
  z-index: 0;

  .slide {
    border-radius: 8px;
    width: 100%;
    height: 100%;
    object-fit: cover;

    &.gallery {
      border-radius: 16px;
      overflow: hidden;
      width: 100%;
      height: 100%;

      > video {
        border-radius: 16px;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }

  .carousel__indicator {
    cursor: pointer;
  }
}

.fullscreen {
  z-index: 9999;
  opacity: 0;
  pointer-events: none;
  background-color: rgba(0, 0, 0, 0.5);

  transition: opacity 0.3s ease-in-out;

  &.open {
    pointer-events: auto;
    opacity: 1;
  }

  & .fullscreen-body {
    > * {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  }
}
</style>
