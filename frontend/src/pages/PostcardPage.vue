<script setup lang="ts">
import { Head, usePage } from "@node_modules/@inertiajs/vue3";

const page = usePage();
page.props["navbarSize"] = "small";

interface PostcardPageProps {
  backgroundColor?: string;
}

const { backgroundColor = "#ffbaba" } = defineProps<PostcardPageProps>();
</script>

<template>
  <Head :title="$t('postcard.title')" />

  <div
    class="h-100 overflow-hidden d-flex justify-content-center align-items-center pb-2"
    :style="{ backgroundColor: backgroundColor }"
    style="padding-top: 4rem"
  >
    <div class="container-xxl postcard-wrapper">
      <div class="postcard">
        <div class="postcard-front">
          <iconify-icon icon="twemoji:teddy-bear" />

          <div class="postcard-stamp"></div>
        </div>
        <div class="postcard-back">
          <h1 class="text-center mb-4">{{ $t("postcard.title") }}</h1>
          <p class="text-center">{{ $t("postcard.description") }}</p>
        </div>
      </div>
    </div>

    <div
      class="position-absolute bottom-0 start-0 end-0 mb-2 d-flex justify-content-center"
    >
      <BButton variant="primary" size="lg" class="btn-circle">
        <iconify-icon icon="streamline:send-email" />
      </BButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
.postcard-wrapper {
  background-color: transparent;
  width: 100%;
  height: 100%;
  max-width: 400px;
  max-height: 400px;
  perspective: 1000px;
}

.postcard {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);

  border-radius: 2rem;
}

.postcard-wrapper:hover .postcard {
  transform: rotateY(180deg);
}

.postcard-front,
.postcard-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;

  border-radius: 2rem;

  border: 2px dashed #e57373;
  padding: 2rem 3rem;
}

.postcard-front {
  background: #fff;
  color: black;

  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 8rem;

  .postcard-stamp {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 50px;
    height: 50px;

    border-radius: 0.5rem;
    border: 2px dashed #e5b473;
  }
}

.postcard-back {
  background: #fff;
  color: black;
  transform: rotateY(180deg);
}
</style>
