<script setup lang="ts">
interface FlipCardProps {
  disableDefaultEvents?: boolean;
  wrapperClass?: string;
  cardClass?: string;
  frontClass?: string;
  backClass?: string;
  maxWidth?: string;
  maxHeight?: string;
  disabled?: boolean;
  changeScale?: boolean;
}

const { maxWidth = "400px", maxHeight = "400px" } = defineProps<FlipCardProps>();

const show = defineModel<boolean>('show', { default: false });
</script>

<template>
  <div
    :class="['flipcard-wrapper', wrapperClass, { show, disabled }]"
    :style="{
      maxWidth, maxHeight,
      '--flipcard-back-scale': changeScale ? '0.8' : '1',
      '--flipcard-front-scale': '1',
    }"
    :title="$t('postcard.open')"
    @click="show = !show && !disableDefaultEvents && !disabled"
  >
    <div :class="['flipcard', cardClass]">
      <div :class="['flipcard-front', frontClass]">
        <slot name="front">
          front
        </slot>
      </div>
      <div :class="['flipcard-back', backClass]">
        <slot name="back">
          back
        </slot>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.flipcard-wrapper {
  width: 100%;
  height: 100%;
  perspective: 1000px;

  background-color: transparent;

  cursor: pointer;

  &.disabled {
    cursor: not-allowed;
  }
}

.flipcard {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;

  color: #333333;
  background-color: #ffffff;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.18);

  transform-style: preserve-3d;
  transform: scale(var(--flipcard-back-scale, 0.8));
  transition: transform 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

.flipcard-wrapper.show .flipcard {
  transform: rotateY(180deg) scale(var(--flipcard-front-scale, 1));
}

.flipcard-front,
.flipcard-back {
  position: absolute;
  width: 100%;
  height: 100%;

  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.flipcard-front {
  display: flex;
  justify-content: center;
  align-items: center;
}

.flipcard-back {
  transform: rotateY(180deg);

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>