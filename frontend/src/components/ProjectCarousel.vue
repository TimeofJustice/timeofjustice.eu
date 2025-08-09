<script setup lang="ts">
import { onBeforeUnmount, ref } from "vue";
import { Carousel, Slide } from "vue3-carousel";
import { TranslatedText } from "@/types/TranslatedText.ts";
import { ProjectImage } from "@/types/ProjectImage.ts";

interface CarouselProps {
  items: ProjectImage[];
}

const { items } = defineProps<CarouselProps>();
const currentSlide = ref(0);
const currentItem = ref<ProjectImage | null>(
  items.length > 0 ? items[0] : null,
);
const isMouseOver = ref(false);
const isFullscreenOpen = ref(false);

const galleryConfig = {
  itemsToShow: 1,
  wrapAround: true,
  mouseDrag: false,
  touchDrag: false,
  height: 320,
  slideEffect: "fade" as const,
};

const thumbnailsConfig = {
  height: 80,
  itemsToShow: 6,
  wrapAround: true,
  touchDrag: false,
  gap: 10,
};

const stopVideo = (el: HTMLVideoElement) => {
  if (!el) return;

  el.pause();
  el.currentTime = 0;
};

const slideTo = (nextSlide: number) => {
  currentSlide.value = nextSlide;
  currentItem.value = items[nextSlide % items.length];

  const prevVideo = document.getElementById(
    "carousel-player-" +
      ((currentSlide.value - 1 + items.length) % items.length),
  ) as HTMLVideoElement;
  stopVideo(prevVideo);
};

const isVideoPlaying = () => {
  const video = document.getElementById(
    "carousel-player-" + (currentSlide.value % items.length),
  ) as HTMLVideoElement;
  return (
    video &&
    video.currentTime > 0 &&
    !video.paused &&
    !video.ended &&
    video.readyState > 2
  );
};

const nextSlide = () => {
  if (!isMouseOver.value && !isVideoPlaying() && !isFullscreenOpen.value)
    slideTo(currentSlide.value + 1);
};

const autoSlideInterval = ref(setInterval(nextSlide, 5000));

onBeforeUnmount(() => {
  clearInterval(autoSlideInterval.value);
});

const openFullscreen = () => {
  isFullscreenOpen.value = true;

  stopVideo(
    document.getElementById(
      "carousel-player-" + (currentSlide.value % items.length),
    ) as HTMLVideoElement,
  );
};

const closeFullscreen = () => {
  const video = document.getElementById("modal-player") as HTMLVideoElement;

  stopVideo(video);

  isFullscreenOpen.value = false;
};

const forceSlideUpdate = (index: number) => {
  slideTo(index);

  clearInterval(autoSlideInterval.value);
  autoSlideInterval.value = setInterval(nextSlide, 5000);
};
</script>

<template>
  <div
    v-if="items.length"
    @mouseover="isMouseOver = true"
    @mouseleave="isMouseOver = false"
  >
    <Carousel v-bind="galleryConfig" v-model="currentSlide" class="mb-2">
      <Slide v-for="(image, i) in items" :key="i">
        <v-lazy-image
          class="slide gallery"
          :src="image.image.original"
          :src-placeholder="image.image.lazy"
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
            :id="`carousel-player-` + i"
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
    </Carousel>

    <Carousel
      v-bind="thumbnailsConfig"
      v-model="currentSlide"
      class="carousel-gradient"
    >
      <Slide v-for="(image, i) in items" :key="i">
        <template #default="{ currentIndex, isActive, isClone }">
          <div
            :class="['thumbnail', { 'is-active': isActive && !isClone }]"
            class="position-relative"
            @click="forceSlideUpdate(currentIndex)"
            :id="currentIndex"
          >
            <div
              class="position-absolute z-1 w-100 h-100 d-flex justify-content-center align-items-center fs-2 text-dark"
              v-if="image.video"
            >
              <iconify-icon icon="fa6-solid:play" class="text-light" />
            </div>
            <v-lazy-image
              class="slide thumbnail-image"
              :src="image.image.original"
              :src-placeholder="image.image.lazy"
              :alt="image.alt[$i18n.locale as keyof TranslatedText]"
            />
          </div>
        </template>
      </Slide>

      <template #addons>
        <BButton
          variant="primary"
          class="btn-circle ms-1 carousel__prev"
          @click="forceSlideUpdate(currentSlide - 1)"
        >
          <iconify-icon icon="fa6-solid:chevron-left" />
        </BButton>
        <BButton
          variant="primary"
          class="btn-circle me-1 carousel__next"
          @click="forceSlideUpdate(currentSlide + 1)"
        >
          <iconify-icon icon="fa6-solid:chevron-right" />
        </BButton>
      </template>
    </Carousel>
  </div>

  <BModal
    v-model="isFullscreenOpen"
    header-class="justify-content-end"
    body-class="overflow-hidden d-flex justify-content-center"
    :hide-footer="true"
    scrollable
    size="xl"
    centered
  >
    <div class="rounded d-flex">
      <v-lazy-image
        class="img-fluid rounded"
        :src="currentItem?.image.original"
        :src-placeholder="currentItem?.image.lazy"
        :alt="currentItem?.alt[$i18n.locale as keyof TranslatedText]"
        v-if="!currentItem?.video"
      />
      <video
        class="img-fluid rounded"
        :src="currentItem?.video"
        controls
        playsinline
        id="modal-player"
        v-else
      />
    </div>

    <template #header>
      <BButton
        variant="tertiary"
        class="btn-square text-light"
        @click="closeFullscreen()"
      >
        <iconify-icon icon="ep:close-bold" />
      </BButton>
    </template>
  </BModal>
</template>
