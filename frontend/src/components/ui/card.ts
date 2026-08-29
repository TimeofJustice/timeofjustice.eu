import type { InjectionKey, Ref } from "vue";

/**
 * Whether the surrounding `UiCard` has a header, provided by it and read by
 * `UiCardBody`.
 *
 * The line between header and body belongs to the body: a `no-body` card puts
 * its body inside a `UiCollapse`, and a line that lived on the header would
 * stay behind as a rule under nothing once that collapsed. The body cannot see
 * the header from where it sits, so the answer is handed down.
 */
export const CARD_HAS_HEADER: InjectionKey<Ref<boolean>> =
  Symbol("card-has-header");
