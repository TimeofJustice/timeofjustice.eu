<script setup lang="ts">
import { Head, usePage } from "@node_modules/@inertiajs/vue3";
import { ref } from "vue";

const page = usePage();
page.props["navbarSize"] = "small";

interface PostcardPageProps {
  backgroundColor?: string;
}

const { backgroundColor = "#ffbaba" } = defineProps<PostcardPageProps>();

const showPostcard = ref(false);
</script>

<template>
  <Head :title="$t('postcard.title')" />

  <div
    class="h-100 overflow-hidden d-flex justify-content-center align-items-center pb-2"
    :style="{ backgroundColor: backgroundColor }"
    style="padding-top: 4rem"
  >
    <div
      class="container-xxl postcard-wrapper"
      :class="{ show: showPostcard }"
      @click="showPostcard = !showPostcard"
    >
      <div class="postcard">
        <div class="postcard-front">
          <iconify-icon icon="twemoji:teddy-bear" />

          <div class="postcard-stamp"></div>
        </div>
        <div class="postcard-back">
          <div class="postcard-message">
            Du es ist so toll! Ich wollte dir nur sagen, wie sehr ich dich
            schätze und wie viel du mir bedeutest. Du bist ein wunderbarer
            Mensch und ich bin so froh, dass wir uns kennen.
          </div>
          <div class="postcard-sender mt-3">Mit viel Liebe, dein Freund</div>
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
@keyframes shake {
  0% {
    transform: rotate(0);
  }
  10% {
    transform: rotate(-5deg);
  }
  20% {
    transform: rotate(5deg);
  }
  30% {
    transform: rotate(-5deg);
  }
  50% {
    transform: rotate(0);
  }
  100% {
    transform: rotate(0);
  }
}

.postcard-wrapper {
  background-color: transparent;
  width: 100%;
  height: 100%;
  max-width: 400px;
  max-height: 400px;
  perspective: 1000px;
  cursor: pointer;
  animation: shake 2s ease-in-out infinite;

  &.show {
    animation: none;
  }
}

.postcard {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55);
  transform-style: preserve-3d;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.18);
  border-radius: 2rem;
  transform: scale(0.8);
}

.postcard-wrapper.show .postcard {
  transform: rotateY(180deg) scale(1);
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
  box-shadow: 0 2px 8px 0 rgba(229, 115, 115, 0.08);
}

.postcard-front {
  background: linear-gradient(135deg, #fff 80%, #ffe5e5 100%);
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
    background: #fffbe6;
    box-shadow: 0 2px 6px 0 rgba(229, 180, 115, 0.12);
  }
}

.postcard-back {
  background: linear-gradient(135deg, #fff 80%, #ffe5e5 100%);
  color: #333;
  transform: rotateY(180deg);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-size: 1.2rem;
  padding: 2rem 2.5rem;
  gap: 1.5rem;

  .postcard-message {
    font-weight: 500;
    margin-bottom: 0.5rem;
    word-break: break-word;
    text-align: center;
    letter-spacing: 0.02em;
  }

  .postcard-sender {
    font-style: italic;
    color: #e57373;
    text-align: center;
    font-family: "Dancing Script", "Segoe Script", cursive;
    font-size: 1.1rem;
    letter-spacing: 0.04em;
  }
}
</style>
