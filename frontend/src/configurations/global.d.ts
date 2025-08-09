import "bootstrap-vue-next";
import { ColorVariant } from "@node_modules/bootstrap-vue-next/dist/src/types/ColorTypes";

declare module "bootstrap-vue-next" {
  export type CustomBadgeVariant =
    | ColorVariant
    // Custom variants
    | "aquamarin"
    | "blue-grey"
    | "brown"
    | "dark-green"
    | "dark-red";

  export interface BBadgeProps {
    variant?: CustomBadgeVariant | null;
  }

  export type CustomButtonVariant = "primary" | "secondary" | "tertiary";

  export interface BaseButtonVariant
    extends Record<CustomButtonVariant, unknown> {
    primary: unknown;
    secondary: unknown;
    tertiary: unknown;
  }

  export type ButtonVariant = keyof BaseButtonVariant;
}
