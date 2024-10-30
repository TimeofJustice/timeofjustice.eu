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

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faGithub, faInstagram, faLinkedin, faTwitter } from "@fortawesome/free-brands-svg-icons";
import { faArrowLeft, faArrowRight, faMaximize, faMinimize, faTimes } from "@fortawesome/free-solid-svg-icons";

library.add(faGithub, faInstagram, faLinkedin, faTwitter, faArrowRight, faTimes, faMaximize, faMinimize, faArrowLeft);

const i18n = createI18n({
    legacy: false,
    locale: (localStorage.getItem("lang") || "en"),
    fallbackLocale: "en",
    messages: { de, en, yoda },
});

import BasicLayout from "@layouts/BasicLayout.vue";

createInertiaApp({
    title: title => `${title} - timeofjustice.eu`,
    resolve: name => {
        const pages = import.meta.glob('./pages/**/*.vue', { eager: true })
        let page = pages[`./pages/${name}.vue`]
        page.default.layout = page.default.layout || BasicLayout
        return page
    },
    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .use(createBootstrap())
            .component('font-awesome-icon', FontAwesomeIcon)
            .use(MotionPlugin)
            .use(i18n)
            .mount(el);
    },
});