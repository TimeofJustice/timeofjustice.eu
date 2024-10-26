import "vite/modulepreload-polyfill";
import { createApp, h } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { MotionPlugin } from '@vueuse/motion'

import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"

createInertiaApp({
    title: title => `${title} - timeofjustice.eu`,
    resolve: (name) => import(`./pages/${name}.vue`),
    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .use(MotionPlugin)
            .mount(el);
    },
});