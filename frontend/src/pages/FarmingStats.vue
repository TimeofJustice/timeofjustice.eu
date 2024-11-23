<script setup lang="ts">
import {useI18n} from "vue-i18n";
import { ref } from 'vue'
import { Crop } from '@/types/Crop.vue'
import { TranslatedText } from "../types/TranslatedText.vue";

interface Props {
  crops: Crop[]
}

const i18n = useI18n();

const { crops } = defineProps<Props>()

const selectedCrop = ref<Crop>(crops[0])

const options = ref({
  chart: {
    type: 'line'
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%',
      endingShape: 'rounded'
    },
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    show: true,
    width: 2,
    colors: ['black'],
  },
  xaxis: {
    categories: [
      i18n.t('farming_stats.month.january'),
      i18n.t('farming_stats.month.february'),
      i18n.t('farming_stats.month.march'),
      i18n.t('farming_stats.month.april'),
      i18n.t('farming_stats.month.may'),
      i18n.t('farming_stats.month.june'),
      i18n.t('farming_stats.month.july'),
      i18n.t('farming_stats.month.august'),
      i18n.t('farming_stats.month.september'),
      i18n.t('farming_stats.month.october'),
      i18n.t('farming_stats.month.november'),
      i18n.t('farming_stats.month.december')
    ]
  },
  yaxis: {
    title: {
      text: i18n.t('farming_stats.price')
    }
  },
  fill: {
    opacity: 1,
  },
  tooltip: {
    y: {
      formatter: function (val: string) {
        return "$ " + val + " thousands"
      }
    }
  },
  annotations: {
    xaxis: [
      {
        x: i18n.t('farming_stats.month.' + selectedCrop.value.harvest_month.start),
        x2: i18n.t('farming_stats.month.' + selectedCrop.value.harvest_month.end),
        fillColor: '#c1470d',
        label: {
          text: i18n.t('farming_stats.harvest_season'),
        }
      },
      {
        x: i18n.t('farming_stats.month.' + selectedCrop.value.planting_month.start),
        x2: i18n.t('farming_stats.month.' + selectedCrop.value.planting_month.end),
        fillColor: '#82ab0d',
        opacity: 0.4,
        label: {
          text: i18n.t('farming_stats.planting_season'),
        }
      },
    ],
    points:
      [
        {
          x: i18n.t('farming_stats.month.' + selectedCrop.value.best_selling_month.month),
          y: selectedCrop.value.best_selling_month.price,
          marker: {
            size: 8,
          },
          label: {
            borderColor: '#82ab0d',
            text: i18n.t('farming_stats.best_selling_price'),
          }
        },
        {
          x: i18n.t('farming_stats.month.' + selectedCrop.value.best_buying_month.month),
          y: selectedCrop.value.best_buying_month.price,
          marker: {
            size: 8,
          },
          label: {
            borderColor: '#0d4cab',
            text: i18n.t('farming_stats.best_buying_price'),
          }
        }
      ]
  }
})

const series = ref([
  {
    type: 'line',
    name: i18n.t('farming_stats.price'),
    data: selectedCrop.value.prices
  }
])

const updateGraph = (crop: Crop) => {
  selectedCrop.value = crop
  series.value = [
    {
      type: 'line',
      name: i18n.t('farming_stats.price'),
      data: crop.prices
    }
  ]
  options.value = {
    ...options.value,
    annotations: {
      xaxis: [
        {
          x: i18n.t('farming_stats.month.' + crop.harvest_month.start),
          x2: i18n.t('farming_stats.month.' + crop.harvest_month.end),
          fillColor: '#c1470d',
          label: {
            text: i18n.t('farming_stats.harvest_season'),
          }
        },
        {
          x: i18n.t('farming_stats.month.' + crop.planting_month.start),
          x2: i18n.t('farming_stats.month.' + crop.planting_month.end),
          fillColor: '#82ab0d',
          opacity: 0.4,
          label: {
            text: i18n.t('farming_stats.planting_season'),
          }
        },
      ],
      points:
        [
          {
            x: i18n.t('farming_stats.month.' + crop.best_selling_month.month),
            y: crop.best_selling_month.price,
            marker: {
              size: 8,
            },
            label: {
              borderColor: '#82ab0d',
              text: i18n.t('farming_stats.best_selling_price'),
            }
          },
          {
            x: i18n.t('farming_stats.month.' + crop.best_buying_month.month),
            y: crop.best_buying_month.price,
            marker: {
              size: 8,
            },
            label: {
              borderColor: '#0d4cab',
              text: i18n.t('farming_stats.best_buying_price'),
            }
          }
        ]
    }
  }
}

</script>

<template>
  <div class="d-flex flex-column-reverse flex-lg-row gap-2 container">
    <div class="col-lg-3">
      <ul class="nav nav-pills flex-column gap-2">
        <li class="nav-item" v-for="crop in crops" :key="crop.name.en" @click="selectedCrop = crop">
          <a class="w-100 btn btn-primary" role="button" :class="{ active: selectedCrop === crop }" @click="updateGraph(crop)">
            {{ crop.name[$i18n.locale as keyof TranslatedText] }}
          </a>
        </li>
      </ul>
    </div>
    <div class="d-flex w-100 h-100 justify-content-center position-sticky top-0">
      <div class="card w-100">
        <apexchart width="100%" type="line" :options="options" :series="series"></apexchart>
      </div>
    </div>
  </div>
</template>