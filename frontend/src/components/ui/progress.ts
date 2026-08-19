import type { InjectionKey, Ref } from "vue";

/** Provided by `UiProgress`, read by the nested `UiProgressBar`. */
export const PROGRESS_MAX: InjectionKey<Ref<number>> = Symbol("progress-max");
