import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'fw-bold',
  routes: [
    {
      path: "/",
      redirect: to => {
        return { path: "/projects" };
      }
    },
    {
      path: '/projects',
      name: 'Projects',
      component: HomeView
    },
  ]
})

router.beforeEach((to, from, next) => {
  document.title = `${String(to.name)} - TimeofJustice`;
  next();
});

export default router
