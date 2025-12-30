import { LazyImage } from "./LazyImage.ts";

export interface ProjectImage {
  image: LazyImage;
  video?: string;
  alt: string;
}
