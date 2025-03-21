<script setup lang="ts">
import 'vue3-carousel/carousel.css'
import { Carousel, Slide } from 'vue3-carousel'
import { TranslatedText } from "@/types/TranslatedText.ts";
import { ProjectImage } from "@/types/ProjectImage.ts";
import { ref } from "vue";
import { faArrowLeft, faArrowRight } from "@fortawesome/free-solid-svg-icons";

interface CarouselProps {
  items: ProjectImage[];
}

defineProps<CarouselProps>()

const currentSlide = ref(0)
const mouseOver = ref(false)

const slideTo = (nextSlide: number) => (currentSlide.value = nextSlide)

// Simulates the autoplay feature to reduce the jumping effect from the thumbnails
setInterval(() => {
  if (!mouseOver.value) slideTo((currentSlide.value + 1))
}, 5000);

const galleryConfig = {
  itemsToShow: 1,
  wrapAround: true,
  mouseDrag: false,
  touchDrag: false,
  height: 320,
  slideEffect: 'fade' as const,
}

const thumbnailsConfig = {
  height: 80,
  itemsToShow: 6,
  wrapAround: true,
  touchDrag: false,
  gap: 10,
}
</script>

<template>
  <div v-if="items.length" @mouseover="mouseOver = true" @mouseleave="mouseOver = false">
    <Carousel v-bind="galleryConfig" v-model="currentSlide" class="mb-2">
      <Slide v-for="(image, i) in items" :key="i">
        <v-lazy-image class="gallery-image" :src="image.image.original" :src-placeholder="image.image.lazy" :alt="image.alt[$i18n.locale as keyof TranslatedText]" />
      </Slide>
    </Carousel>

    <Carousel v-bind="thumbnailsConfig" v-model="currentSlide">
      <Slide v-for="(image, i) in items" :key="i">
        <template #default="{ currentIndex, isActive, isClone }">
          <div
            :class="['thumbnail', { 'is-active': isActive && !isClone }]"
            @click="slideTo(currentIndex)"
            :id="currentIndex"
          >
            <v-lazy-image class="thumbnail-image" :src="image.image.original" :src-placeholder="image.image.lazy" :alt="image.alt[$i18n.locale as keyof TranslatedText]" />
          </div>
        </template>
      </Slide>

      <template #addons>
        <BButton variant="secondary" class="btn-circle ms-1 carousel__prev" @click="slideTo(currentSlide - 1)">
          <font-awesome-icon :icon="faArrowLeft" />
        </BButton>
        <BButton variant="secondary" class="btn-circle me-1 carousel__next" @click="slideTo(currentSlide + 1)">
          <font-awesome-icon :icon="faArrowRight" />
        </BButton>
      </template>
    </Carousel>
  </div>
</template>

<style scoped lang="scss">
:root {
  background-color: #242424;
}

.carousel {
  --vc-nav-background: rgba(255, 255, 255, 0.7);
  --vc-nav-border-radius: 100%;
}

img {
  border-radius: 8px;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.gallery-image {
  border-radius: 16px;
}

.thumbnail {
  height: 95%;
  width: 95%;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s ease-in-out, height 0.3s ease-in-out, width 0.3s ease-in-out;
}

.thumbnail.is-active,
.thumbnail:hover {
  opacity: 1;
  height: 100%;
  width: 100%;
}
</style>