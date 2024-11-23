<script lang="ts">
import { TranslatedText } from "./TranslatedText.vue";

interface MonthPrice {
  month: string,
  price: number
}

interface MonthPhase {
  start: string,
  end: string
}

export interface Crop {
    name: TranslatedText,
    harvest_month: MonthPhase,
    planting_month: MonthPhase,
    prices: number[],
    best_selling_month: MonthPrice,
    best_buying_month: MonthPrice
  }
</script>