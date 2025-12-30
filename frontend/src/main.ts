import { createApp, DefineComponent, h } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { MotionPlugin } from "@vueuse/motion";
import { createI18n } from "vue-i18n";
import { createBootstrap } from "bootstrap-vue-next";
import VLazyImage from "v-lazy-image";
import VueMarkdown from "vue-markdown-render";
import Vue3Marquee from "vue3-marquee";
import axios from "axios";

import { Icon } from "@iconify/vue";
import bootstrapVueNextConfig from "@configurations/bootstrapVueNext";

import de from "@assets/locales/de.json";
import en from "@assets/locales/en.json";
import yoda from "@assets/locales/en-yoda.json";

import "@assets/scss/_index.scss";
import "bootstrap";
import "vue-color/style.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";

import BaseLayout from "@layouts/BaseLayout.vue";
import BaseLink from "@components/BaseLink.vue";

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem("lang") || "en",
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
      .use(createBootstrap(bootstrapVueNextConfig))
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
