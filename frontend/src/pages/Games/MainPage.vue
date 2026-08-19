<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { useToast } from "@composables/toast";
import { useI18n } from "@node_modules/vue-i18n";
import { ref, shallowRef } from "vue";
import { onBeforeUnmount } from "@node_modules/vue";
import { useWallet } from "@composables/wallet";
import axios from "axios";

import HigherOrLower from "@components/Games/HigherOrLower.vue";
import RideTheBus from "@components/Games/RideTheBus.vue";
import BlackJack from "@components/Games/BlackJack.vue";
import SicBo from "@components/Games/SicBo.vue";
import GamesLeaderboardPosition from "@components/GamesLeaderboardPosition.vue";
import GamesAvatar from "@components/GamesAvatar.vue";
import GamesDailyReward from "@components/GamesDailyReward.vue";
import { TOAST_TRANSITION } from "@components/ui/transitions";

interface Player {
  name: string;
  balance: number;
  streak: number;
}

interface DailyBonus {
  day: number;
  reward: number;
  status: "locked" | "unlocked" | "claimed";
}

interface MainProps {
  leaderboard: Player[];
  ownPosition: number;
  newBonus: boolean;
  nextBonus: string;
  dailyBonus: DailyBonus[];
  vault: number;
  vaultReset: string;
  hintDismissed: boolean;
}

const i18n = useI18n();
const { create } = useToast();

const {
  leaderboard,
  ownPosition,
  newBonus,
  nextBonus,
  vault,
  vaultReset,
  hintDismissed,
} = defineProps<MainProps>();

const { wallet, balance, balanceChange, changeBalance, openSettings } =
  useWallet();

const gameComponent = shallowRef<object>(HigherOrLower);
const gameComponents = new Map<string, object>([
  ["higher_lower", HigherOrLower],
  ["ride_the_bus", RideTheBus],
  ["black_jack", BlackJack],
  ["sic_bo", SicBo],
]);

const updatedLeaderboard = ref<Player[]>(leaderboard);
const updatedOwnPosition = ref(ownPosition);
const updatedVault = ref(vault);

const showCopyReminder = ref(!hintDismissed);
const showDisclaimer = ref(true);
const showDailyBonus = ref(newBonus);
const showGames = ref(true);
const showLeaderboard = ref(false);
const showGamesAccount = ref(false);

const waitingForResponse = ref(false);

const nextBonusDate = ref(new Date(nextBonus));
const vaultResetDate = ref(new Date(vaultReset));
const bonusTimer = ref("");
const vaultTimer = ref("");

const getTimer = (date: Date) => {
  const now = new Date();
  const diff = date.getTime() - now.getTime();

  if (diff <= 0) {
    return "00:00:00";
  }

  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
};

bonusTimer.value = getTimer(nextBonusDate.value);
const nextBonusCounter = setInterval(() => {
  bonusTimer.value = getTimer(nextBonusDate.value);
}, 1000);
vaultTimer.value = getTimer(vaultResetDate.value);
const vaultCounter = setInterval(() => {
  vaultTimer.value = getTimer(vaultResetDate.value);
}, 1000);

const showToast = (message: string, variant: "success" | "danger") => {
  create({ body: message, variant, position: "bottom-start" });
};

const redeemDailyBonus = () => {
  waitingForResponse.value = true;

  axios
    .post("/games/api/user/redeem/")
    .then((response) => {
      showToast(
        i18n.t("games.main.reward_redeemed", { reward: response.data.reward }),
        "success",
      );

      showDailyBonus.value = false;
      nextBonusDate.value = new Date(response.data.nextBonus);
      changeBalance(response.data.reward);
      waitingForResponse.value = false;
    })
    .catch((error) => {
      showToast(i18n.t(error.response.data.error), "danger");

      waitingForResponse.value = false;
    });
};

const leaderBoardFetch = setInterval(() => {
  if (document.hidden) return;

  axios.get("/games/api/leaderboard/").then((response) => {
    updatedLeaderboard.value = response.data.leaderboard;
    updatedOwnPosition.value = response.data.ownPosition;
  });
}, 10000);

const vaultFetch = setInterval(() => {
  if (document.hidden) return;

  axios.get("/games/api/vault/").then((response) => {
    vaultResetDate.value = new Date(response.data.vaultReset);
    updatedVault.value = response.data.vault;
  });
}, 10000);

onBeforeUnmount(() => {
  clearInterval(leaderBoardFetch);
  clearInterval(nextBonusCounter);
  clearInterval(vaultCounter);
  clearInterval(vaultFetch);
});

const dismissHint = () => {
  showCopyReminder.value = false;

  axios.post("/games/api/hint/dismiss/").catch((error) => {
    console.error("Failed to dismiss hint:", error);
  });
};
</script>

<template>
  <Head :title="$t('games.title')" />

  <UiModal
    v-model="showDailyBonus"
    header-class="justify-between items-center"
    body-class="flex flex-col gap-2"
    scrollable
    centered
  >
    <template #header>
      <h2 class="m-0">
        {{ $t("games.main.daily_bonus") }}
      </h2>

      <UiButton
        variant="tertiary"
        class="text-light"
        @click="showDailyBonus = false"
        square
      >
        <iconify-icon icon="ep:close-bold" />
      </UiButton>
    </template>

    <div class="flex flex-wrap justify-between gap-2">
      <GamesDailyReward
        :day="bonus.day"
        :reward="bonus.reward"
        :status="bonus.status"
        v-for="bonus in dailyBonus"
        :key="bonus.day"
        :overflow="bonus.day > 5"
      />
    </div>

    <UiButton
      variant="success"
      class="w-full"
      @click="redeemDailyBonus"
      :disabled="waitingForResponse"
    >
      {{ $t("games.main.redeem") }}
    </UiButton>
  </UiModal>

  <div class="container-page flex flex-col justify-center pb-4 lg:flex-row">
    <div class="w-full shrink-0 lg:w-3/4">
      <KeepAlive>
        <component
          :is="gameComponent"
          :balance="balance"
          @balance-change="changeBalance"
        />
      </KeepAlive>
    </div>

    <div
      class="flex w-full shrink-0 flex-col gap-2 pt-2 md:flex-row lg:w-1/4 lg:flex-col lg:pt-0 lg:pl-2"
    >
      <div class="flex w-full shrink-0 flex-col gap-2 md:w-1/2 lg:w-full">
        <Transition v-bind="TOAST_TRANSITION">
          <UiToast
            v-if="showCopyReminder"
            variant="danger"
            body-class="flex items-center justify-between gap-2"
            class="w-full"
          >
            <div>{{ $t("games.main.reminder") }}</div>

            <UiButton variant="tertiary" @click="dismissHint" square>
              <iconify-icon icon="ep:close-bold" />
            </UiButton>
          </UiToast>
        </Transition>

        <UiCard
          header-class="flex items-center justify-between"
          body-class="flex flex-col"
        >
          <template #header>
            <div class="flex min-w-0 items-center gap-2">
              <GamesAvatar :avatar="wallet.avatar" size="md" />

              <h4 class="m-0 truncate">
                {{ wallet.name }}
              </h4>
            </div>

            <div class="flex gap-2">
              <UiButton variant="tertiary" @click="openSettings" square>
                <iconify-icon icon="fa7-solid:edit" />
              </UiButton>
              <UiButton variant="danger" to="/logout/" square>
                <iconify-icon icon="fa7-solid:sign-out" />
              </UiButton>
            </div>
          </template>

          <div class="flex items-center gap-1">
            <iconify-icon icon="fa7-solid:coins" />
            <strong>{{ balance }} TJTs</strong>

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

          <small
            class="text-accent"
            v-if="bonusTimer !== '00:00:00' && bonusTimer !== ''"
          >
            {{ $t("games.main.next_bonus_in", { time: bonusTimer }) }}
          </small>
          <small class="text-warning" v-else-if="bonusTimer !== ''">
            {{ $t("games.main.next_bonus") }}
          </small>
        </UiCard>

        <UiCard
          header-class="flex items-center justify-between relative"
          no-body
        >
          <template #header>
            <h4 class="m-0">
              <iconify-icon icon="fa7-solid:vault" />
              {{ $t("games.main.vault") }}
            </h4>

            <UiButton
              variant="tertiary"
              class="after:absolute after:inset-0 after:z-1 after:content-['']"
              @click="showGamesAccount = !showGamesAccount"
              square
            >
              <iconify-icon
                icon="fa6-solid:chevron-up"
                :style="{
                  transform: !showGamesAccount
                    ? 'rotate(180deg)'
                    : 'rotate(0deg)',
                }"
                class="transition-transform duration-300 ease-in-out"
              />
            </UiButton>
          </template>

          <UiCollapse v-model="showGamesAccount">
            <UiCardBody class="flex flex-col gap-2">
              <div class="flex items-center justify-between gap-1">
                <div
                  class="flex items-center gap-1"
                  :class="updatedVault >= 0 ? 'text-success' : 'text-danger'"
                >
                  <iconify-icon icon="fa7-solid:coins" />
                  <strong>{{ updatedVault }} TJTs</strong>
                </div>
              </div>

              <small class="text-accent" v-if="vaultTimer !== ''">
                {{ $t("games.main.vault_reset_in", { time: vaultTimer }) }}
              </small>
            </UiCardBody>
          </UiCollapse>
        </UiCard>
      </div>

      <div class="flex w-full shrink flex-col gap-2 md:w-1/2 lg:w-full">
        <UiCard
          header-class="flex items-center justify-between relative"
          no-body
        >
          <template #header>
            <h4 class="m-0">
              <iconify-icon icon="fa7-solid:dice" />
              {{ $t("games.main.games") }}
            </h4>

            <UiButton
              variant="tertiary"
              class="after:absolute after:inset-0 after:z-1 after:content-['']"
              @click="showGames = !showGames"
              square
            >
              <iconify-icon
                icon="fa6-solid:chevron-up"
                :style="{
                  transform: !showGames ? 'rotate(180deg)' : 'rotate(0deg)',
                }"
                class="transition-transform duration-300 ease-in-out"
              />
            </UiButton>
          </template>

          <UiCollapse v-model="showGames">
            <UiCardBody class="flex flex-col gap-2">
              <UiButton
                variant="secondary"
                @click="gameComponent = Comp"
                :active="gameComponent === Comp"
                v-for="([name, Comp], index) in gameComponents"
                :key="index"
              >
                {{ $t("games.game." + name + ".title") }}
              </UiButton>
            </UiCardBody>
          </UiCollapse>
        </UiCard>

        <UiCard
          header-class="flex items-center justify-between relative"
          no-body
        >
          <template #header>
            <h4 class="m-0">
              <iconify-icon icon="fa7-solid:trophy" />
              {{ $t("games.main.leaderboard") }}
            </h4>

            <UiButton
              variant="tertiary"
              class="after:absolute after:inset-0 after:z-1 after:content-['']"
              @click="showLeaderboard = !showLeaderboard"
              square
            >
              <iconify-icon
                icon="fa6-solid:chevron-up"
                :style="{
                  transform: !showLeaderboard
                    ? 'rotate(180deg)'
                    : 'rotate(0deg)',
                }"
                class="transition-transform duration-300 ease-in-out"
              />
            </UiButton>
          </template>

          <UiCollapse v-model="showLeaderboard">
            <UiCardBody class="flex flex-col gap-2">
              <GamesLeaderboardPosition
                v-for="(player, index) in updatedLeaderboard"
                :key="index"
                :index="index + 1"
                :name="player.name"
                :balance="player.balance"
                :streak="player.streak"
                :highlighted="index + 1 === updatedOwnPosition"
              />

              <template v-if="updatedOwnPosition > 5">
                <div class="text-center font-bold">
                  <iconify-icon icon="fa7-solid:ellipsis" />
                </div>

                <GamesLeaderboardPosition
                  :index="updatedOwnPosition"
                  :name="wallet.name"
                  :balance="balance"
                  :streak="wallet.streak"
                  highlighted
                />
              </template>
            </UiCardBody>
          </UiCollapse>
        </UiCard>
      </div>
    </div>
  </div>

  <div
    class="pointer-events-none fixed inset-x-0 bottom-0 z-3 container-fixed"
    v-if="showDisclaimer"
  >
    <UiAlert
      v-model="showDisclaimer"
      class="pointer-events-auto"
      variant="danger"
      dismissible
    >
      <template #close>
        <iconify-icon icon="ep:close-bold" />
      </template>

      <vue-markdown :source="$t('games.entry.warning')" />
    </UiAlert>
  </div>
</template>

<style scoped>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
