import { TranslatedText } from "./TranslatedText.js";
import { LazyImage } from "./LazyImage.ts";

export interface ProjectImage {
  image: LazyImage;
  alt: TranslatedText;
}