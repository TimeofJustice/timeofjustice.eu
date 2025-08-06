/**
 * Configuration file for FontAwesome.
 * This file imports FontAwesome icons and adds them to the library to be used globally in the application.
 * Refer to the documentation for more details:
 * https://docs.fontawesome.com/apis/javascript/import-icons
 */

import { library } from "@fortawesome/fontawesome-svg-core";
import {
  faGithub,
  faInstagram,
  faLinkedin,
  faTwitter,
  faVuejs,
} from "@fortawesome/free-brands-svg-icons";
import {
  faExternalLinkAlt,
  faGlobe,
  faTimes,
} from "@fortawesome/free-solid-svg-icons";

library.add(
  faGithub,
  faInstagram,
  faLinkedin,
  faTwitter,
  faTimes,
  faVuejs,
  faGlobe,
  faExternalLinkAlt,
);
