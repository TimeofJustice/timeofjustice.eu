<script setup lang="ts">
import { usePage } from "@node_modules/@inertiajs/vue3";

const page = usePage();
page.props["navbarSize"] = "small";
</script>

<template>
  <div class="d-flex container-xxl gap-2 flex-column flex-lg-row mb-2 justify-content-center align-items-center h-100">
    <div class="wrapper">
      <div class="lid one"></div>
      <div class="lid two"></div>
      <div class="envelope"></div>
      <div class="letter">
        <p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.wrapper {
  height: 200px;
  width: 300px;
  background-color: #3760C9;
  position: relative;
  display: flex;
  justify-content: center;
  z-index: 0;
}

.lid {
  position: absolute;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
  border-right: 150px solid transparent;
  border-bottom: 100px solid transparent;
  border-left: 150px solid transparent;
  transform-origin: top;
  transition: transform 0.25s linear;
}

/* Lid when closed */
.lid.one {
  border-top: 100px solid #658ced;
  transform: rotateX(0deg);
  z-index: 3;
  transition-delay: 0.75s;
}

/* Lid when opened */
.lid.two {
  border-top: 100px solid #3760C9;
  transform: rotateX(90deg);
  z-index: 1;
  transition-delay: 0.5s;
}

.envelope {
  position: absolute;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
  border-top: 100px solid transparent;
  border-right: 150px solid #C4DFF0;
  border-bottom: 100px solid #C4DFF0;
  border-left: 150px solid #a4d4f2;
  z-index: 3;
}

.letter {
  position: absolute;
  top: 0;
  width: 80%;
  height: 80%;
  background-color: white;
  border-radius: 15px;
  z-index: 2;
  transition: 0.5s;

  padding: 20px;
  overflow: auto;
}

.letter p {
  text-align: center;
  font-size: 16px;
  color: #3B4049;
}

.wrapper:hover .lid.one {
  transform: rotateX(90deg);
  transition-delay: 0s;
}

.wrapper:hover .lid.two {
  transform: rotateX(180deg);
  transition-delay: 0.25s;
}

@keyframes pullLetter {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-100%);
  }
}

.letter {
  animation: pullLetter 0.5s alternate;
  animation-play-state: paused;
}

.wrapper:hover .letter {
  animation-play-state: running;
  animation-delay: 0.5s;
}
</style>