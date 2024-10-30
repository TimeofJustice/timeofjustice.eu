<script setup lang="ts">
import Project from "./ProjectDetails.vue";
import { ref } from "vue";

interface Props {
  project: Project;
}

defineProps<Props>();

const imgSize = ref(250);
const imgButton = ref("fa-maximize");

const handleResize = () => {
  if (imgSize.value === 500) {
    imgSize.value = 250;
    imgButton.value = "fa-maximize";
  } else {
    imgSize.value = 500;
    imgButton.value = "fa-minimize";
  }
};
</script>

<template>
  <div class="position-relative button-on-hover" v-if="project">
    <BCarousel controls indicators ride="carousel" interval="2500" :img-height="imgSize" class="resizeable">
      <BCarouselSlide img-src="https://picsum.photos/1024/480/?image=1" class="img-fluid" />
      <BCarouselSlide img-src="https://picsum.photos/1024/480/?image=2" class="img-fluid" />
      <BCarouselSlide img-src="https://picsum.photos/1024/480/?image=3" class="img-fluid" />
      <BCarouselSlide :img-src="require('@assets/images/TimeofJustice.jpg')" class="img-fluid" />
    </BCarousel>

    <div class="position-absolute top-0 end-0 m-2 btn btn-primary z-3" @click="handleResize">
      <font-awesome-icon :icon="['fa-solid', imgButton]" />
    </div>
  </div>

  <div class="w-100 h-100 d-flex justify-content-center align-items-center" v-else>
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>