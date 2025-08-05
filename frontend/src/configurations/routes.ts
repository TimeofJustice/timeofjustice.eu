/**
 * Configuration file for application routes.
 * This file defines the routes used in the application, including their names, paths, icons
 * and the components that represent them.
 */

import { Route } from "../types/Route.ts";
import {
  faDice,
  faHome,
  faPaintBrush,
} from "@node_modules/@fortawesome/free-solid-svg-icons";

export const ROUTES: Route[] = [
  {
    name: "nav.projects",
    path: "/",
    icon: faHome,
    activeComponents: ["ProjectsPage"],
  },
  {
    name: "nav.games",
    path: "/games/",
    icon: faDice,
    activeComponents: [
      "Games/GamesPage",
      "Games/GamesEntry",
      "Games/GamesLogin",
    ],
  },
  {
    name: "nav.place",
    path: "/r-place/",
    icon: faPaintBrush,
    activeComponents: ["RPlace"],
    isHighlighted: true,
  },
];
