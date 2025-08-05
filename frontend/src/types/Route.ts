import { IconDefinition } from "@fortawesome/fontawesome-common-types";

export interface Route {
  name: string;
  path: string;
  icon: IconDefinition;
  activeComponents: string[];
  isHighlighted?: boolean;
}
