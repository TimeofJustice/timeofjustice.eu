import { DirectiveBinding } from "vue";

function updateVisibility(el: HTMLElement, binding: DirectiveBinding): void {
  el.hidden = !binding.value;
}

export const wip = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    updateVisibility(el, binding);
  },
  updated(el: HTMLElement, binding: DirectiveBinding) {
    updateVisibility(el, binding);
  },
};
