import { onBeforeUnmount, readonly, ref } from "vue";

/**
 * Tracks a CSS media query from script. For painting, use a Tailwind breakpoint
 * class; this is for when the breakpoint changes *what* is rendered, which CSS
 * cannot tell the template.
 */
export const useMediaQuery = (query: string) => {
  const matches = ref(false);

  if (typeof window === "undefined" || !window.matchMedia)
    return readonly(matches);

  const media = window.matchMedia(query);

  matches.value = media.matches;

  const onChange = (event: MediaQueryListEvent) => {
    matches.value = event.matches;
  };

  media.addEventListener("change", onChange);
  onBeforeUnmount(() => media.removeEventListener("change", onChange));

  return readonly(matches);
};
