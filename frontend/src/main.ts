import "vite/modulepreload-polyfill";
import { createApp, h } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { MotionPlugin } from '@vueuse/motion'
import { createI18n } from "vue-i18n";
import {createBootstrap} from 'bootstrap-vue-next'

import "@node_modules/flag-icons/css/flag-icons.min.css";
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"

import "@assets/scss/index.scss";

import de from "@assets/locales/de.json";
import en from "@assets/locales/en.json";
import yoda from "@assets/locales/yoda.json";

const i18n = createI18n({
    legacy: false,
    locale: (localStorage.getItem("lang") || "en"),
    fallbackLocale: "en",
    messages: { de, en, yoda },
});

createInertiaApp({
    title: title => `${title} - timeofjustice.eu`,
    resolve: (name) => import(`@pages/${name}.vue`),
    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .use(createBootstrap())
            .use(MotionPlugin)
            .use(i18n)
            .mount(el);
    },
});