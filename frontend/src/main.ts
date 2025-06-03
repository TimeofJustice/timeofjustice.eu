import { createApp, h } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { MotionPlugin } from '@vueuse/motion'
import { createI18n } from "vue-i18n";
import { createBootstrap } from 'bootstrap-vue-next'
import VLazyImage from "v-lazy-image";
import VueMarkdown from 'vue-markdown-render'
import Vue3Marquee from 'vue3-marquee'
import Link from "@components/Link.vue";

import "@assets/scss/_index.scss";
import 'bootstrap';

import de from "@assets/locales/de.json";
import en from "@assets/locales/en.json";
import yoda from "@assets/locales/yoda.json";

import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import "@configurations/FontAwesome";
import bootstrapVueNextConfig from '@configurations/bootstrapVueNext';
import axios from 'axios';

import { Calendar, DatePicker } from 'v-calendar';
import 'v-calendar/style.css';

import 'bootstrap-vue-next/dist/bootstrap-vue-next.css';

const i18n = createI18n({
    legacy: false,
    locale: (localStorage.getItem("lang") || "en"),
    fallbackLocale: "en",
    messages: { de, en, yoda },
});

import BasicLayout from "@layouts/BasicLayout.vue";
import { wip } from "@/directives/wip.ts";
import VueApexCharts from "@node_modules/vue3-apexcharts";

axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

createInertiaApp({
    title: title => `${title} - timeofjustice.eu`,
    resolve: (name) => {
        const pages = import.meta.glob('./pages/**/*.vue', { eager: true })
        let page: any = pages[`./pages/${name}.vue`]
        // Use default layout if none is set
        page.default.layout = page.default.layout || BasicLayout
        return page
    },
    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .use(createBootstrap(bootstrapVueNextConfig))
            .component('font-awesome-icon', FontAwesomeIcon)
            .component('v-lazy-image', VLazyImage)
            .component('vue-markdown', VueMarkdown)
            .use(MotionPlugin)
            .use(i18n)
            .use(VueApexCharts)
            .use(Vue3Marquee)
            .directive('wip', wip)
            .component('Link', Link)
            .component('VCalendar', Calendar)
            .component('VDatePicker', DatePicker)
            .provide('$router', 'fake')
            .mount(el);
    },
});