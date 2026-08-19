import { createApp, DefineComponent, h } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { MotionPlugin } from "@vueuse/motion";
import { createI18n } from "vue-i18n";
import VLazyImage from "v-lazy-image";
import VueMarkdown from "vue-markdown-render";
import Vue3Marquee from "vue3-marquee";
import axios from "axios";

import { Icon } from "@iconify/vue";

import de from "@assets/locales/de.json";
import en from "@assets/locales/en.json";
import yoda from "@assets/locales/en-yoda.json";

import "@fontsource/inter";
import "@fontsource/inter/100.css";
import "@fontsource/inter/200.css";
import "@fontsource/inter/300.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import "@fontsource/inter/900.css";
import "@fontsource/inter/100-italic.css";
import "@fontsource/inter/200-italic.css";
import "@fontsource/inter/300-italic.css";
import "@fontsource/inter/400-italic.css";
import "@fontsource/inter/500-italic.css";
import "@fontsource/inter/600-italic.css";
import "@fontsource/inter/700-italic.css";
import "@fontsource/inter/800-italic.css";
import "@fontsource/inter/900-italic.css";

import "@assets/css/index.css";

import BaseLayout from "@layouts/BaseLayout.vue";
import BaseLink from "@components/BaseLink.vue";
import { getCookie } from "@composables/cookie";

const i18n = createI18n({
  legacy: false,
  locale: getCookie("django_language") || "en",
  fallbackLocale: "en",
  messages: { de, en, "en-yoda": yoda },
});

axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

createInertiaApp({
  title: (title) => `${title} - timeofjustice.eu`,
  resolve: (name) => {
    const pages = import.meta.glob("./pages/**/*.vue", { eager: true });
    const page = pages[`./pages/${name}.vue`] as { default: DefineComponent };
    page.default.layout = page.default.layout || BaseLayout;
    return page;
  },
  setup({ el, App, props, plugin }) {
    createApp({ render: () => h(App, props) })
      .use(plugin)
      .component("iconify-icon", Icon)
      .component("v-lazy-image", VLazyImage)
      .component("vue-markdown", VueMarkdown)
      .use(MotionPlugin)
      .use(i18n)
      .use(Vue3Marquee)
      .component("BaseLink", BaseLink)
      .provide("$router", "fake")
      .mount(el);
  },
});
