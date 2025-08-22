<script setup lang="ts">
import { Head } from "@node_modules/@inertiajs/vue3";

import FlipCard from "@components/FlipCard.vue";
</script>

<template>
  <Head :title="$t('cards.title')" />

  <div
    class="h-100 overflow-hidden bg-light d-flex flex-column"
    style="padding-top: 4rem"
  >
<!--    Top Container-->
    <div class="d-flex flex-row align-items-center bg-green-500 gap-4">
      <!--    Black Card Container-->
      <div class="bg-pink-200 p-1">
        <FlipCard card-class="rounded-3" style="height: 18rem; width: 18rem">
          <template #front>
            <div class="black-front rounded-3">
              <h5 class="text-center">{{ $t("cards.front") }}</h5>
            </div>
          </template>

          <template #back>
            <div class="black-back">
              <h1 class="text-center">{{ $t("cards.back") }}</h1>
            </div>
          </template>
        </FlipCard>
      </div>
    </div>

<!--    Card Deck Container-->
    <div class="bg-red-500 flex-grow-1 d-grid gap-3 h-100 p-1"
         style="grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr))">
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
      <FlipCard card-class="rounded-3" style="aspect-ratio: 1/1; width: 100%;">
        <template #front>
          <div class="white-front rounded-3">
            <h5 class="text-center">{{ $t("cards.front") }}</h5>
          </div>
        </template>

        <template #back>
          <div class="white-back">
            <h1 class="text-center">{{ $t("cards.back") }}</h1>
          </div>
        </template>
      </FlipCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
.black-front {
  background-color: black;
  color: white;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
