<script setup lang="ts">
import { onMounted, onUnmounted, ref, useTemplateRef } from "vue";
import { ROUTES } from "@configurations/routes.ts";

import LocaleDropdown from "@components/LocaleDropdown.vue";
import BaseNavbarLink from "@components/BaseNavbarLink.vue";
import GamesWalletBadge from "@components/GamesWalletBadge.vue";

import TimeofJusticeLogo from "@assets/images/TimeofJustice.svg";

interface BaseNavbarProps {
  size?: "normal" | "small";
}

const { size = "normal" } = defineProps<BaseNavbarProps>();

const isScrolled = ref(false);
const showNavOffcanvas = ref(false);

const bar = useTemplateRef<HTMLElement>("bar");

/**
 * How wide the collapsed pill has to be, in pixels. Measured rather than written
 * down, because a sixth route or a wider flag changes it, and a fixed 26rem let
 * the content spill out of the pill.
 *
 * Read synchronously with the bar forced into its collapsed state, so no paint
 * happens in between.
 */
const collapsedWidth = ref<number>();

let queued = false;

const measure = () => {
  queued = false;

  const element = bar.value;

  if (!element) return;

  // `still` goes on first and comes off last: reading the collapsed width
  // forces the browser to work out that layout, and without it the bar would
  // animate into the measured width and back out of it again.
  element.classList.add("still");
  element.classList.add("measuring");

  const width = Math.ceil(element.getBoundingClientRect().width);

  element.classList.remove("measuring");
  // Settle back into the real width before motion is allowed again.
  void element.offsetWidth;
  element.classList.remove("still");

  collapsedWidth.value = width;
};

/** Coalesces the bursts: fonts, avatar and balance all land within a frame. */
const remeasure = () => {
  if (queued) return;

  queued = true;
  requestAnimationFrame(measure);
};

onMounted(() => {
  const parent: HTMLElement =
    document.querySelector(".content-body") ?? document.documentElement;
  const onScroll = () => {
    isScrolled.value = parent.scrollTop > 0;
  };

  parent.addEventListener("scroll", onScroll);
  window.addEventListener("resize", remeasure);

  // Whatever changes inside the bar changes how wide it needs to be: a route
  // list, a translated label, the balance ticking up after a win.
  const contents = new MutationObserver(remeasure);

  if (bar.value) {
    contents.observe(bar.value, {
      subtree: true,
      childList: true,
      characterData: true,
    });
  }

  measure();
  // The first measurement runs on fallback metrics; Inter arrives later.
  document.fonts?.ready.then(remeasure);

  onUnmounted(() => {
    parent.removeEventListener("scroll", onScroll);
    window.removeEventListener("resize", remeasure);
    contents.disconnect();
  });
});
</script>

<template>
  <div
    class="pointer-events-none top-0 z-1 flex w-full flex-wrap content-center items-center justify-center py-2 lg:flex-nowrap"
    :class="size === 'small' ? 'absolute' : 'sticky'"
  >
    <div
      ref="bar"
      class="navbar-body pointer-events-auto container-page flex flex-row items-center justify-between gap-2"
      :class="{
        'scrolled relative min-w-0 bg-card shadow-card backdrop-blur-card':
          isScrolled || size === 'small',
      }"
      :style="
        collapsedWidth ? { '--navbar-collapsed': `${collapsedWidth}px` } : {}
      "
    >
      <!-- Menu and brand travel together, so the logo is never wedged between
           the controls on the right. On lg the button disappears and the logo
           is left alone on the left, where it has always been. -->
      <div class="flex items-center gap-2">
        <UiButton
          variant="tertiary"
          square
          class="text-control-lg leading-none lg:hidden"
          @click="showNavOffcanvas = true"
        >
          <iconify-icon icon="fa6-solid:bars" />
        </UiButton>

        <div class="py-1.25 text-control-lg whitespace-nowrap">
          <v-lazy-image
            class="brand-picture h-auto max-w-full rounded-md"
            :src="TimeofJusticeLogo"
            :alt="$t('nav.brand_alt')"
          />
        </div>
      </div>

      <div class="hidden w-full items-center justify-between lg:flex">
        <div class="flex items-center gap-1">
          <BaseNavbarLink
            :route="route"
            v-for="route in ROUTES"
            :key="route.name"
          />
        </div>

        <LocaleDropdown />
      </div>

      <div class="flex items-center gap-1">
        <LocaleDropdown class="block lg:hidden" />

        <GamesWalletBadge />
      </div>
    </div>

    <div class="pointer-events-auto flex lg:hidden">
      <UiOffcanvas
        v-model="showNavOffcanvas"
        placement="start"
        class="w-full sm:w-75"
        :teleport-disabled="true"
      >
        <template #header>
          <UiButton
            variant="tertiary"
            square
            :title="$t('general.close')"
            @click="showNavOffcanvas = false"
          >
            <iconify-icon icon="ep:close-bold" />
          </UiButton>
        </template>

        <div class="flex flex-col" @click="showNavOffcanvas = false">
          <BaseNavbarLink
            :route="route"
            v-for="route in ROUTES"
            :key="route.name"
          />
        </div>
      </UiOffcanvas>
    </div>
  </div>
</template>

<style scoped>
.brand-picture {
  width: 2.3rem;
  min-width: 2.3rem;
  height: 2.3rem;
  min-height: 2.3rem;
}

/*
 * On scroll the bar collapses into a compact pill. Below xxl there is no room
 * for that, so only the surface treatment changes.
 */
.navbar-body {
  margin: 0;
  border-radius: var(--radius-surface);

  transition:
    backdrop-filter 0.3s ease-in-out,
    background 0.3s ease-in-out,
    box-shadow 0.3s ease-in-out,
    padding 0.3s ease-in-out,
    margin 0.3s ease-in-out;
}

.navbar-body.scrolled {
  padding-left: 0.3125rem;
  padding-right: 0.3125rem;
  margin-left: 0.4375rem;
  margin-right: 0.4375rem;
}

@media (min-width: 1400px) {
  .navbar-body {
    /* A spring on `width` overshoots, which on the way in would dip below the
       width the icons need. This is the floor the bounce lands on. */
    min-width: var(--navbar-collapsed, 0px);

    transition:
      width 0.8s cubic-bezier(0.68, -0.55, 0.27, 1.55),
      backdrop-filter 0.3s ease-in-out,
      background 0.3s ease-in-out,
      box-shadow 0.3s ease-in-out,
      padding 0.3s ease-in-out,
      margin 0.3s ease-in-out;
  }

  .navbar-body.scrolled {
    /* A third of the page container, less a gap: the column the profile card
       stands in on the home page, so the two end level. The measured width is
       the floor, not the target. */
    width: max(
      var(--navbar-collapsed, 0px),
      calc(var(--container-page) / 3 - 1.5rem)
    );
  }

  .navbar-body :deep(.link-title) {
    max-width: 10rem;
    margin-left: 0.25rem;
    overflow: hidden;

    transition:
      max-width 0.3s ease-in-out,
      margin-left 0.3s ease-in-out;
    transition-delay: 0.2s;
  }

  .navbar-body.scrolled :deep(.link-title) {
    max-width: 0;
    margin-left: 0;
    transition-delay: 0s;
  }

  /* The links close ranks as the titles go, which is where the spring finds its
     room: it swings some 84px past the collapsed width. Same curve and delays as
     the titles, so the two read as one movement. */
  .navbar-body :deep(.nav-link) {
    transition: padding 0.3s ease-in-out;
    transition-delay: 0.2s;
  }

  .navbar-body.scrolled :deep(.nav-link) {
    padding-inline: 0.25rem;
    transition-delay: 0s;
  }
}

/*
 * The collapsed state, held for the length of one synchronous read so the bar
 * can be asked how wide it wants to be. Last in the file on purpose: both rules
 * have to beat the widths set above them, which carry the same specificity.
 */
.navbar-body.still,
.navbar-body.still :deep(.link-title) {
  transition: none;
}

.navbar-body.measuring {
  width: max-content;
  /* Without this the last measurement would be the floor of the next one, and
     a bar that lost a route could never measure itself smaller again. */
  min-width: 0;
  padding-left: 0.3125rem;
  padding-right: 0.3125rem;
}

.navbar-body.measuring :deep(.link-title) {
  max-width: 0;
  margin-left: 0;
}

.navbar-body.measuring :deep(.nav-link) {
  padding-inline: 0.25rem;
}
</style>
