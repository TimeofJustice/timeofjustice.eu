import { reactive, readonly } from "vue";
import type { Variant } from "@components/ui/variants";

export type ToastPosition =
  | "top-start"
  | "top-center"
  | "top-end"
  | "middle-start"
  | "middle-center"
  | "middle-end"
  | "bottom-start"
  | "bottom-center"
  | "bottom-end";

export interface ToastOptions {
  body: string;
  variant?: Variant;
  position?: ToastPosition;
  /** Milliseconds until the toast disappears. Pass 0 to keep it around. */
  duration?: number;
}

export interface Toast extends Required<Omit<ToastOptions, "duration">> {
  id: number;
}

const toasts = reactive<Toast[]>([]);

let nextId = 0;

const remove = (id: number) => {
  const index = toasts.findIndex((toast) => toast.id === id);

  if (index !== -1) toasts.splice(index, 1);
};

const create = ({
  body,
  variant = "secondary",
  position = "bottom-start",
  duration = 5000,
}: ToastOptions) => {
  const id = nextId++;

  toasts.push({ id, body, variant, position });

  if (duration > 0) setTimeout(() => remove(id), duration);

  return id;
};

/**
 * Queues transient messages. `UiToaster` — rendered once in the layout — picks
 * them up and takes care of positioning and dismissal.
 */
export const useToast = () => ({
  toasts: readonly(toasts),
  create,
  remove,
});
