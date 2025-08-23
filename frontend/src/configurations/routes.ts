/**
 * Configuration file for application routes.
 * This file defines the routes used in the application, including their names, paths, icons
 * and the components that represent them.
 */

import { Route } from "../types/Route.ts";

export const ROUTES: Route[] = [
  {
    name: "nav.projects",
    path: "/",
    icon: "fa6-solid:house",
    activeComponents: ["ProjectsPage"],
  },
  {
    name: "nav.games",
    path: "/games/",
    icon: "fa7-solid:dice",
    activeComponents: [
      "Games/MainPage",
      "Games/EntryPage",
      "Games/LoginPage",
    ],
  },
  {
    name: "nav.place",
    path: "/r-place/",
    icon: "fa6-solid:paintbrush",
    activeComponents: ["RPlace"],
  },
  {
    name: "nav.postcard",
    path: "/sendy/",
    icon: "bi:envelope-heart-fill",
    activeComponents: ["PostcardPage"],
    isHighlighted: true,
  },
  {
    name: "nav.cards",
    path: "/cards/",
    icon: "streamline:cards-remix",
    activeComponents: ["Cards/MainPage"],
    isHighlighted: true,
  },
];
