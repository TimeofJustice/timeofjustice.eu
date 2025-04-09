<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import {
  faChevronUp,
  faClose, faCoins,
  faCopy,
  faDice,
  faEdit,
  faEllipsis,
  faSignOut,
  faTrophy, faUser,
  faWallet
} from "@node_modules/@fortawesome/free-solid-svg-icons";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController/index";
import { useI18n } from "@node_modules/vue-i18n";
import { reactive, ref, shallowRef } from "vue";
import HigherOrLower from "@pages/Casino/Games/HigherOrLower.vue";
import RideTheBus from "@pages/Casino/Games/RideTheBus.vue";
import { computed } from "@node_modules/vue";
import axios from "axios";

const { show } = useToastController()

interface Player {
  name: string;
  balance: number;
}

interface Props {
  wallet: Wallet;
  leaderboard: Player[];
  your_position: number;
}

const i18n = useI18n();

const { wallet } = defineProps<Props>();
const showPlus = ref(0);
const showMinus = ref(0);

const copyToClipboard = () => {
  navigator.clipboard.writeText(wallet.wallet_id)
    .then(() => {
      show?.({
        props: {
          body: i18n.t('casino.main.copy_wallet'),
          variant: "success",
          interval: 5000,
          pos: "bottom-start",
        }
      });
    })
    .catch(_ => {
      show?.({
        props: {
          body: i18n.t('casino.main.copy_wallet_error'),
          variant: "danger",
          interval: 5000,
          pos: "bottom-start",
        }
      });
    });
};

const showCopyReminder = ref(true);

const gameComponent = shallowRef<object>(HigherOrLower);

const onTokenWon = (tokens: number) => {
  wallet.balance += tokens;
  showPlus.value = tokens;

  setTimeout(() => {
    showPlus.value = 0;
  }, 1000);
};

const onTokenLost = (tokens: number) => {
  wallet.balance -= tokens;
  showMinus.value = tokens;

  setTimeout(() => {
    showMinus.value = 0;
  }, 1000);
};

const showGames = ref(true);
const showLeaderboard = ref(false);
const showSettings = ref(false);

const form = reactive({
  name: wallet.name
});

const validation = computed(() => {
  if (form.name.trim() === "")
    return false;

  return /^[a-zA-Z0-9]{3,32}$/.test(form.name);
});

const waitingForResponse = ref(false);

const save = async () => {
  if (validation.value) {
    waitingForResponse.value = true;

    axios.post('/casino/api/user/change/', {
      name: form.name,
    }).then(response => {
      wallet.name = response.data.name;

      show?.({
        props: {
          body: i18n.t('casino.main.settings_success'),
          variant: "success",
          interval: 5000,
          pos: "bottom-start",
        }
      });

      waitingForResponse.value = false;
    }).catch(error => {
      show?.({
        props: {
          body: i18n.t(error.response.data.error),
          variant: "danger",
          interval: 5000,
          pos: "bottom-start",
        }
      });

      waitingForResponse.value = false;
    });
  }
};
</script>

<template>
  <Head :title="$t('casino.title')" />

  <BModal data-bs-theme="dark" v-model="showSettings" header-class="justify-content-between align-items-center"
          :hide-footer="true" :no-close-on-backdrop="true" scrollable :no-close-on-esc="true" size="md" centered>
    <template #header>
      <h2 class="m-0">
        {{ $t('casino.main.settings') }}
      </h2>

      <BButton variant="tertiary" class="btn-square text-light" @click="showSettings = false">
        <font-awesome-icon :icon="faClose" />
      </BButton>
    </template>

    <BForm @submit.prevent="save" class="d-flex flex-column gap-2 w-100">
      <BFormGroup id="input-group-2" label-for="input-2">
        <BFormInput id="input-2" v-model="form.name" :placeholder="$t('casino.login.enter_wallet')" required :state="validation" />
        <BFormInvalidFeedback :state="validation">
          {{ $t('casino.main.settings_invalid') }}
        </BFormInvalidFeedback>
      </BFormGroup>

      <BButton type="submit" variant="primary" class="w-100" :disabled="!validation || waitingForResponse">
        {{ $t('general.save') }}
      </BButton>
    </BForm>
  </BModal>

  <div class="container-xxl text-white d-flex gap-2 justify-content-center">
    <div class="row w-100 g-2">
      <div class="col-9">
        <component :is="gameComponent" :balance="Number(wallet.balance)" @tokens_won="onTokenWon" @tokens_lost="onTokenLost" />
      </div>

      <div class="col-3 d-flex flex-column gap-2">
        <BToast :model-value="showCopyReminder" variant="danger" body-class="d-flex align-items-center justify-content-between gap-2">
          <div>{{ $t('casino.main.reminder') }}</div>

          <BButton variant="tertiary" class="btn-square" @click="showCopyReminder = false">
            <font-awesome-icon :icon="faClose"/>
          </BButton>
        </BToast>

        <BCard class="bg-grey-100 bg-opacity-50" header-class="d-flex align-items-center justify-content-between" body-class="d-flex flex-column">
          <template #header>
            <h4 class="m-0 text-truncate">
              <font-awesome-icon :icon="faUser"/>
              {{ wallet.name }}
            </h4>

            <div class="d-flex gap-2">
              <BButton variant="tertiary" class="btn-square" @click="showSettings = true">
                <font-awesome-icon :icon="faEdit" />
              </BButton>
              <BButton variant="danger" class="btn-square" to="/casino/logout/">
                <font-awesome-icon :icon="faSignOut" />
              </BButton>
            </div>
          </template>

          <div class="d-flex align-items-center gap-2 justify-content-between position-relative">
            <span class="text-truncate d-flex gap-1 align-items-center">
              <font-awesome-icon :icon="faWallet"/>
              {{ wallet.wallet_id.slice(0, 10) }}...
            </span>

            <BButton variant="tertiary" class="btn-square stretched-link" @click="copyToClipboard()">
              <font-awesome-icon :icon="faCopy" />
            </BButton>
          </div>

          <div class="d-flex gap-1 align-items-center">
            <font-awesome-icon :icon="faCoins"/>
            <strong>{{ wallet.balance }} TJTs</strong>

            <Transition>
              <span class="text-success" v-if="showPlus">
                +{{ showPlus }} TJTs
              </span>
            </Transition>
            <Transition>
              <span class="text-danger" v-if="showMinus">
                -{{ showMinus }} TJTs
              </span>
            </Transition>
          </div>
        </BCard>

        <BCard class="bg-grey-100 bg-opacity-50" header-class="d-flex align-items-center justify-content-between position-relative" no-body>
          <template #header>
            <h4 class="m-0">
              <font-awesome-icon :icon="faDice"/>
              {{ $t('casino.main.games') }}
            </h4>

            <BButton variant="tertiary" class="btn-square stretched-link" @click="showGames = !showGames">
              <font-awesome-icon :icon="faChevronUp" :style="{ transform: !showGames ? 'rotate(180deg)' : 'rotate(0deg)' }" class="transition-transform" />
            </BButton>
          </template>

          <BCollapse v-model="showGames">
            <BCardBody class="d-flex flex-column gap-2">
              <BButton @click="gameComponent = HigherOrLower" :active="gameComponent === HigherOrLower">
                {{ $t('casino.game.higher_lower.title') }}
              </BButton>
              <BButton @click="gameComponent = RideTheBus" :active="gameComponent === RideTheBus">
                {{ $t('casino.game.ride_the_bus.title') }}
              </BButton>
            </BCardBody>
          </BCollapse>
        </BCard>

        <BCard class="bg-grey-100 bg-opacity-50" header-class="d-flex align-items-center justify-content-between position-relative" no-body>
          <template #header>
            <h4 class="m-0">
              <font-awesome-icon :icon="faTrophy"/>
              {{ $t('casino.main.leaderboard') }}
            </h4>

            <BButton variant="tertiary" class="btn-square stretched-link" @click="showLeaderboard = !showLeaderboard">
              <font-awesome-icon :icon="faChevronUp" :style="{ transform: !showLeaderboard ? 'rotate(180deg)' : 'rotate(0deg)' }" class="transition-transform" />
            </BButton>
          </template>

          <BCollapse v-model="showLeaderboard">
            <BCardBody class="d-flex flex-column gap-2">
              <div class="bg-grey-200 bg-opacity-50 px-3 py-2 d-flex align-items-center justify-content-between rounded border border-grey-100" v-for="(player, index) in leaderboard" :key="index">
                <span class="fw-bold text-truncate">
                  {{ index + 1 }}. {{ player.name }}
                </span>
                <div class="col-4 text-end">
                  {{ player.balance }} TJTs
                </div>
              </div>

              <template v-if="your_position > 5">
                <div class="fw-bold text-center">
                  <font-awesome-icon :icon="faEllipsis"/>
                </div>

                <div class="bg-grey-200 bg-opacity-50 px-3 py-2 d-flex align-items-center justify-content-between rounded border border-grey-100">
                  <span class="fw-bold text-truncate">
                    {{ your_position }}. You
                  </span>
                  <div class="col-4 text-end">
                    {{ wallet.balance }} TJTs
                  </div>
                </div>
              </template>
            </BCardBody>
          </BCollapse>
        </BCard>
      </div>
    </div>
  </div>

  <BToastOrchestrator />
</template>

<style scoped lang="scss">
  .v-enter-active,
  .v-leave-active {
    transition: opacity 0.5s ease;
  }

  .v-enter-from,
  .v-leave-to {
    opacity: 0;
  }

  .transition-transform {
    transition: transform 0.3s ease;
  }
</style>