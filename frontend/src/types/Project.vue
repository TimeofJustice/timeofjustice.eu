<script lang="ts">
import { TranslatedText } from "./TranslatedText.vue";
import { Technology } from "./Technology.vue";

default export interface Project {
    id: number;
    title: string;
    short_description: TranslatedText,
    description: TranslatedText,
    title_image: string,
    images: string[],
    technologies: Technology[],
    github: string,
    website: string,
  }
</script>