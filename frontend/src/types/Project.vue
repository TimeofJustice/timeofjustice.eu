<script lang="ts">
import { TranslatedText } from "./TranslatedText.vue";
import { Technology } from "./Technology.vue";
import { ProjectImage } from "./ProjectImage.vue";
import { LazyImage } from "./LazyImage.vue";

interface Status {
  name: TranslatedText;
  color: string;
}

export interface Project {
    id: number;
    title: string;
    status: Status;
    short_description: TranslatedText,
    description: TranslatedText,
    title_image: LazyImage,
    images: ProjectImage[],
    technologies: Technology[],
    github: string,
    website: string,
  }
</script>