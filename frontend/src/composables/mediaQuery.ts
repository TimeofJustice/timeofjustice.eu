import { onBeforeUnmount, readonly, ref } from "vue";

/**
 * Tracks a CSS media query from script.
 *
 * For painting, a Tailwind breakpoint class is always the better answer. This
 * is for the cases where the breakpoint changes *what* is rendered rather than
 * how it looks — deciding which column a card belongs to, say, which no amount
 * of CSS can tell the template.
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
