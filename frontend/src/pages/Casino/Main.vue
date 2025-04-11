<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
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
import { computed, onBeforeUnmount } from "@node_modules/vue";
import axios from "axios";
import LeaderboardPosition from "@pages/Casino/components/LeaderboardPosition.vue";
import DailyReward from "@pages/Casino/components/DailyReward.vue";
import BlackJack from "@pages/Casino/Games/BlackJack.vue";

interface Player {
  name: string;
  balance: number;
}

interface DailyBonus {
  day: number;
  reward: number;
  status: "locked" | "unlocked" | "claimed";
}

interface MainProps {
  wallet: Wallet;
  leaderboard: Player[];
  ownPosition: number;
  newBonus: boolean;
  dailyBonus: DailyBonus[];
}

const i18n = useI18n();
const { show } = useToastController();

const { wallet, leaderboard, ownPosition, newBonus } = defineProps<MainProps>();

const gameComponent = shallowRef<object>(HigherOrLower);
const gameComponents = new Map<string, object>([
  ["higher_lower", HigherOrLower],
  ["ride_the_bus", RideTheBus],
  ["black_jack", BlackJack]
]);

const balanceChange = ref(0);
const updatedLeaderboard = ref<Player[]>(leaderboard);
const updatedOwnPosition = ref(ownPosition);

const showCopyReminder = ref(true);
const showSettings = ref(false);
const showDailyBonus = ref(newBonus);
const showGames = ref(true);
const showLeaderboard = ref(false);

const waitingForResponse = ref(false);

const settingsForm = reactive({
  name: wallet.name
});

const validateName = computed(() => {
  if (settingsForm.name.trim() === "")
    return false;

  return /^[a-zA-Z0-9]{3,32}$/.test(settingsForm.name);
});

const showToast = (message: string, variant: "success" | "danger") => {
  show?.({
    props: {
      body: message,
      variant: variant,
      interval: 5000,
      pos: "bottom-start"
    }
  });
};

const saveSettings = async () => {
  if (validateName.value) {
    waitingForResponse.value = true;

    axios.post("/casino/api/user/update/", {
      name: settingsForm.name
    }).then(response => {
      showToast(i18n.t("casino.main.settings_success"), "success");

      wallet.name = response.data.name;
      waitingForResponse.value = false;
    }).catch(error => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
  }
};

const redeemDailyBonus = () => {
  waitingForResponse.value = true;

  axios.post("/casino/api/user/redeem/").then(response => {
    showToast(i18n.t("casino.main.reward_redeemed", {"reward": response.data.reward}), "success");

    showDailyBonus.value = false;
    onBalanceChange(response.data.reward)
    waitingForResponse.value = false;
  }).catch(error => {
    showToast(i18n.t(error.response.data.error), "danger");

    waitingForResponse.value = false;
  });
};

const copyToClipboard = () => {
  navigator.clipboard.writeText(wallet.walletId)
    .then(() => {
      showToast(i18n.t("casino.main.copy_wallet"), "success");
    })
    .catch(_ => {
      showToast(i18n.t("casino.main.copy_wallet_error"), "danger");
    });
};

const onBalanceChange = (tokens: number) => {
  wallet.balance = wallet.balance + tokens;
  balanceChange.value = tokens;

  setTimeout(() => {
    balanceChange.value = 0;
  }, 1000);
};

const leaderBoardFetch = setInterval(() => {
  if (document.hidden)
    return;

  axios.get("/casino/api/leaderboard/").then(response => {
    updatedLeaderboard.value = response.data.leaderboard;
    updatedOwnPosition.value = response.data.ownPosition;
  });
}, 10000)

onBeforeUnmount(() => {
  clearInterval(leaderBoardFetch);
});
</script>

<template>
  <Head :title="$t('casino.title')" />

  <BModal data-bs-theme="dark" v-model="showDailyBonus" header-class="justify-content-between align-items-center" body-class="d-flex flex-column gap-2"
          :hide-footer="true" :no-close-on-backdrop="true" scrollable :no-close-on-esc="true" size="md" centered>
    <template #header>
      <h2 class="m-0">
        {{ $t('casino.main.daily_bonus') }}
      </h2>

      <BButton variant="tertiary" class="btn-square text-light" @click="showDailyBonus = false">
        <font-awesome-icon :icon="faClose" />
      </BButton>
    </template>

    <div class="d-flex gap-2 flex-wrap justify-content-between">
      <DailyReward :day="bonus.day" :reward="bonus.reward" :status="bonus.status" v-for="bonus in dailyBonus" :key="bonus.day" :overflow="bonus.day > 5" />
    </div>

    <BButton variant="success" class="w-100" @click="redeemDailyBonus" :disabled="waitingForResponse">
      {{ $t("casino.main.redeem") }}
    </BButton>
  </BModal>

  <BModal data-bs-theme="dark" v-model="showSettings" header-class="justify-content-between align-items-center"
          :hide-footer="true" :no-close-on-backdrop="true" scrollable :no-close-on-esc="true" size="md" centered>
    <template #header>
      <h2 class="m-0">
        {{ $t("casino.main.settings") }}
      </h2>

      <BButton variant="tertiary" class="btn-square text-light" @click="showSettings = false">
        <font-awesome-icon :icon="faClose" />
      </BButton>
    </template>

    <BForm @submit.prevent="saveSettings" class="d-flex flex-column gap-2 w-100">
      <BFormGroup id="input-group-2" label-for="input-2">
        <BFormInput id="input-2" v-model="settingsForm.name" :placeholder="$t('casino.login.enter_wallet')" required :state="validateName" />
        <BFormInvalidFeedback :state="validateName">
          {{ $t("casino.main.settings_invalid") }}
        </BFormInvalidFeedback>
      </BFormGroup>

      <BButton type="submit" variant="primary" class="w-100" :disabled="!validateName || waitingForResponse">
        {{ $t("general.save") }}
      </BButton>
    </BForm>
  </BModal>

  <div class="container-xxl text-white d-flex gap-2 justify-content-center">
    <div class="row w-100 g-2">
      <div class="col-9">
        <component :is="gameComponent" :balance="wallet.balance" @balanceChange="onBalanceChange" />
      </div>

      <div class="col-3 d-flex flex-column gap-2">
        <BToast :model-value="showCopyReminder" variant="danger" body-class="d-flex align-items-center justify-content-between gap-2">
          <div>{{ $t("casino.main.reminder") }}</div>

          <BButton variant="tertiary" class="btn-square" @click="showCopyReminder = false">
            <font-awesome-icon :icon="faClose" />
          </BButton>
        </BToast>

        <BCard class="bg-grey-100 bg-opacity-50" header-class="d-flex align-items-center justify-content-between" body-class="d-flex flex-column">
          <template #header>
            <h4 class="m-0 text-truncate">
              <font-awesome-icon :icon="faUser" />
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
              <font-awesome-icon :icon="faWallet" />
              {{ wallet.walletId.slice(0, 10) }}...
            </span>

            <BButton variant="tertiary" class="btn-square stretched-link" @click="copyToClipboard()">
              <font-awesome-icon :icon="faCopy" />
            </BButton>
          </div>

          <div class="d-flex gap-1 align-items-center">
            <font-awesome-icon :icon="faCoins" />
            <strong>{{ wallet.balance }} TJTs</strong>

            <Transition>
              <span class="text-success" v-if="balanceChange > 0">
                +{{ balanceChange }} TJTs
              </span>
            </Transition>
            <Transition>
              <span class="text-danger" v-if="balanceChange < 0">
                {{ balanceChange }} TJTs
              </span>
            </Transition>
          </div>
        </BCard>

        <BCard class="bg-grey-100 bg-opacity-50" header-class="d-flex align-items-center justify-content-between position-relative" no-body>
          <template #header>
            <h4 class="m-0">
              <font-awesome-icon :icon="faDice" />
              {{ $t("casino.main.games") }}
            </h4>

            <BButton variant="tertiary" class="btn-square stretched-link" @click="showGames = !showGames">
              <font-awesome-icon :icon="faChevronUp" :style="{ transform: !showGames ? 'rotate(180deg)' : 'rotate(0deg)' }" class="transition-transform" />
            </BButton>
          </template>

          <BCollapse v-model="showGames">
            <BCardBody class="d-flex flex-column gap-2">
              <BButton @click="gameComponent = Comp" :active="gameComponent === Comp" v-for="([name, Comp], index) in gameComponents" :key="index">
                {{ $t("casino.game." + name + ".title") }}
              </BButton>
            </BCardBody>
          </BCollapse>
        </BCard>

        <BCard class="bg-grey-100 bg-opacity-50" header-class="d-flex align-items-center justify-content-between position-relative" no-body>
          <template #header>
            <h4 class="m-0">
              <font-awesome-icon :icon="faTrophy" />
              {{ $t("casino.main.leaderboard") }}
            </h4>

            <BButton variant="tertiary" class="btn-square stretched-link" @click="showLeaderboard = !showLeaderboard">
              <font-awesome-icon :icon="faChevronUp" :style="{ transform: !showLeaderboard ? 'rotate(180deg)' : 'rotate(0deg)' }" class="transition-transform" />
            </BButton>
          </template>

          <BCollapse v-model="showLeaderboard">
            <BCardBody class="d-flex flex-column gap-2">
              <LeaderboardPosition v-for="(player, index) in updatedLeaderboard" :key="index" :index="index + 1" :name="player.name" :balance="player.balance"
                                   :highlighted="index + 1 === updatedOwnPosition" />

              <template v-if="updatedOwnPosition > 5">
                <div class="fw-bold text-center">
                  <font-awesome-icon :icon="faEllipsis" />
                </div>

                <LeaderboardPosition :index="updatedOwnPosition" :name="wallet.name" :balance="wallet.balance" highlighted />
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