<script lang="ts">
import { TranslatedText } from "./TranslatedText.vue";
import { LazyImage } from "./LazyImage.vue";

  export interface ProjectImage {
    image: LazyImage;
    alt: TranslatedText;
  }
</script>