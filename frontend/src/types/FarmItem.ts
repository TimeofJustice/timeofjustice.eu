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
  harvestMonth: MonthPhase;
  plantingMonth: MonthPhase;
  prices: number[];
  bestSellingMonth: MonthPrice;
  bestBuyingMonth: MonthPrice;
}

export interface Commodity {
  name: TranslatedText;
  prices: number[];
  bestSellingMonth: MonthPrice;
  bestBuyingMonth: MonthPrice;
}

export interface FarmItems {
  crops: Crop[];
  commodities: Commodity[];
}
