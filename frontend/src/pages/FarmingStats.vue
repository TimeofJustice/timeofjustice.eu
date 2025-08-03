<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { ref } from "vue";
import { FarmItems } from "@/types/FarmItem.ts";
import { TranslatedText } from "@/types/TranslatedText.ts";
import { ApexOptions } from "apexcharts";
import { Head } from "@inertiajs/vue3";

interface Props {
  farmItems: FarmItems;
}

const i18n = useI18n();

const { farmItems } = defineProps<Props>();
const selectedIndex = ref<number>(0);

const pages = {
  crops: i18n.t("farming_stats.pages.crops"),
  commodities: i18n.t("farming_stats.pages.commodities"),
};
const currentPage = ref(pages.crops);

const getOptions = (index: number) => {
  let newOptions: ApexOptions = {
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "55%",
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      show: true,
      width: 2,
      colors: ["black"],
      curve: "stepline",
    },
    xaxis: {
      categories: [
        i18n.t("farming_stats.month.january"),
        i18n.t("farming_stats.month.february"),
        i18n.t("farming_stats.month.march"),
        i18n.t("farming_stats.month.april"),
        i18n.t("farming_stats.month.may"),
        i18n.t("farming_stats.month.june"),
        i18n.t("farming_stats.month.july"),
        i18n.t("farming_stats.month.august"),
        i18n.t("farming_stats.month.september"),
        i18n.t("farming_stats.month.october"),
        i18n.t("farming_stats.month.november"),
        i18n.t("farming_stats.month.december"),
        i18n.t("farming_stats.month.end_of_december"),
      ],
    },
    yaxis: {
      title: {
        text: i18n.t("farming_stats.price"),
      },
    },
    fill: {
      opacity: 1,
    },
    annotations: {
      xaxis: [],
      points: [],
    },
  };

  switch (currentPage.value) {
    case pages.crops:
      const crop = farmItems.crops[index];

      newOptions = {
        ...newOptions,
        annotations: {
          xaxis: [
            {
              x: i18n.t("farming_stats.month." + crop.harvestMonth.start),
              x2: i18n.t("farming_stats.month." + crop.harvestMonth.end),
              fillColor: "#c1470d",
              label: {
                text: i18n.t("farming_stats.harvest_season"),
              },
            },
            {
              x: i18n.t("farming_stats.month." + crop.plantingMonth.start),
              x2: i18n.t("farming_stats.month." + crop.plantingMonth.end),
              fillColor: "#82ab0d",
              opacity: 0.4,
              label: {
                text: i18n.t("farming_stats.planting_season"),
              },
            },
          ],
          points: [
            {
              x: i18n.t("farming_stats.month." + crop.bestSellingMonth.month),
              y: crop.bestSellingMonth.price,
              marker: {
                size: 8,
              },
              label: {
                borderColor: "#82ab0d",
                text: i18n.t("farming_stats.best_selling_price"),
              },
            },
            {
              x: i18n.t("farming_stats.month." + crop.bestBuyingMonth.month),
              y: crop.bestBuyingMonth.price,
              marker: {
                size: 8,
              },
              label: {
                borderColor: "#0d4cab",
                text: i18n.t("farming_stats.best_buying_price"),
              },
            },
          ],
        },
      };
      break;
    case pages.commodities:
      const commodity = farmItems.commodities[index];

      newOptions = {
        ...newOptions,
        annotations: {
          xaxis: [],
          points: [
            {
              x: i18n.t(
                "farming_stats.month." + commodity.bestSellingMonth.month,
              ),
              y: commodity.bestSellingMonth.price,
              marker: {
                size: 8,
              },
              label: {
                borderColor: "#82ab0d",
                text: i18n.t("farming_stats.best_selling_price"),
              },
            },
            {
              x: i18n.t(
                "farming_stats.month." + commodity.bestBuyingMonth.month,
              ),
              y: commodity.bestBuyingMonth.price,
              marker: {
                size: 8,
              },
              label: {
                borderColor: "#0d4cab",
                text: i18n.t("farming_stats.best_buying_price"),
              },
            },
          ],
        },
      };
      break;
  }

  return newOptions;
};
const getSeries = (index: number) => {
  const newSeries = [];

  switch (currentPage.value) {
    case pages.crops:
      const crop = farmItems.crops[index];

      newSeries.push({
        type: "line",
        name: i18n.t("farming_stats.price"),
        data: crop.prices,
      });
      break;
    case pages.commodities:
      const commodity = farmItems.commodities[index];

      newSeries.push({
        type: "line",
        name: i18n.t("farming_stats.price"),
        data: commodity.prices,
      });
      break;
  }

  return newSeries;
};

const options = ref(getOptions(selectedIndex.value));
const series = ref(getSeries(selectedIndex.value));

const changeIndex = (index: number) => {
  selectedIndex.value = index;
  options.value = getOptions(index);
  series.value = getSeries(index);
};
const changePage = (page: string) => {
  currentPage.value = page;
  selectedIndex.value = 0;
  options.value = getOptions(0);
  series.value = getSeries(0);
};
</script>

<template>
  <Head :title="i18n.t('farming_stats.title')" />

  <div class="container d-flex flex-column gap-2">
    <ul class="nav nav-tabs">
      <li class="nav-item" v-for="(page, key) in pages" :key="key">
        <a
          class="nav-link"
          :class="{ active: currentPage === page }"
          @click="changePage(page)"
        >
          {{ page }}
        </a>
      </li>
    </ul>

    <div class="d-flex flex-column-reverse flex-lg-row gap-2">
      <div class="col-lg-3">
        <ul class="nav nav-pills flex-column gap-2">
          <li
            class="nav-item"
            v-for="(crop, index) in farmItems.crops"
            :key="crop.name.en"
            v-if="currentPage === pages.crops"
          >
            <a
              class="w-100 btn btn-primary"
              role="button"
              :class="{ active: selectedIndex === index }"
              @click="changeIndex(index)"
            >
              {{ crop.name[$i18n.locale as keyof TranslatedText] }}
            </a>
          </li>
          <li
            class="nav-item"
            v-for="(commodity, index) in farmItems.commodities"
            :key="commodity.name.en"
            v-if="currentPage === pages.commodities"
          >
            <a
              class="w-100 btn btn-primary"
              role="button"
              :class="{ active: selectedIndex === index }"
              @click="changeIndex(index)"
            >
              {{ commodity.name[$i18n.locale as keyof TranslatedText] }}
            </a>
          </li>
        </ul>
      </div>
      <div
        class="d-flex w-100 h-100 justify-content-center position-sticky top-0"
      >
        <div class="card w-100">
          <apexchart
            width="100%"
            type="line"
            :options="options"
            :series="series"
          ></apexchart>
        </div>
      </div>
    </div>
  </div>
</template>
