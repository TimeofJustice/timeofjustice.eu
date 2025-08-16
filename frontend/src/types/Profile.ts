import { TranslatedText } from "@/types/TranslatedText.ts";

export interface Profile {
  picture?: string;
  description?: TranslatedText;
  shortDescription?: TranslatedText;
  repository?: string;
}
