<script setup lang="ts">
import { useUi } from "./cn";

export interface UiSkeletonProps {
  /**
   * `text` draws `lines` bars at text height; `circle` and `rect` draw a single
   * shape and take their size from the caller's classes, so a placeholder can
   * be given exactly the box the real thing will occupy.
   */
  variant?: "text" | "circle" | "rect";
  /** `text` only. The last bar is drawn short, the way a paragraph ends. */
  lines?: number;
}

const { variant = "text", lines = 1 } = defineProps<UiSkeletonProps>();

defineOptions({ inheritAttrs: false });

const BAR = "skeleton h-[1em] w-full rounded-md";

// A stack of bars is one placeholder, so for `text` the caller's classes size
// the stack and the bars inside it are left alone. The other two variants have
// nothing inside them: there the wrapper is the shape.
const { ui, rest } = useUi(() =>
  variant === "text"
    ? "flex w-full flex-col gap-2"
    : [
        "skeleton",
        variant === "circle" ? "size-9 rounded-full" : "h-24 w-full",
        variant === "rect" && "rounded-surface",
      ],
);
</script>

<template>
  <!--
    `aria-busy` says the region is pending without putting words to it; the
    words, if this placeholder is worth announcing at all, come from the
    caller's `aria-label`, the way every other string in `ui/` does. A
    placeholder that merely fills a gap next to a heading is better off
    `aria-hidden`.
  -->
  <div :class="ui" role="status" aria-busy="true" v-bind="rest">
    <!-- The variant decides whether there are bars at all, which is a question
         about the whole stack, not about each bar. Kept off the `v-for` because
         the two together read as though the condition were per bar, and a
         condition that did mention `index` would silently not see it. -->
    <template v-if="variant === 'text'">
      <div
        :class="[BAR, index === lines && lines > 1 && 'w-3/5']"
        v-for="index in lines"
        :key="index"
        aria-hidden="true"
      />
    </template>
  </div>
</template>
