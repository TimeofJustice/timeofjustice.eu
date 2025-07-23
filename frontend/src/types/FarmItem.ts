import { TranslatedText } from "./TranslatedText.js";

interface MonthPrice {
  month: string;
  price: number;
}

interface MonthPhase {
  start: string;
  end: string;
}

export interface Crop {
  name: TranslatedText;
  harvest_month: MonthPhase;
  planting_month: MonthPhase;
  prices: number[];
  best_selling_month: MonthPrice;
  best_buying_month: MonthPrice;
}

export interface Commodity {
  name: TranslatedText;
  prices: number[];
  best_selling_month: MonthPrice;
  best_buying_month: MonthPrice;
}

export interface FarmItems {
  crops: Crop[];
  commodities: Commodity[];
}
