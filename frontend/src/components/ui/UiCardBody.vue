<script setup lang="ts">
import { inject, ref } from "vue";
import { CARD_HAS_HEADER } from "./card";

// Defaults to no header, so a body used outside a card - or in one without a
// header - does not draw a line along the card's own top edge.
const hasHeader = inject(CARD_HAS_HEADER, ref(false));
</script>

<template>
  <div class="grow p-4" :class="hasHeader && 'border-t border-hairline'">
    <slot />
  </div>
</template>
