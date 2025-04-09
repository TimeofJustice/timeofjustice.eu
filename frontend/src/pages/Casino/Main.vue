<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import { faClose, faCopy, faDice, faSignOut, faWallet } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController/index";
import { useI18n } from "@node_modules/vue-i18n";
import { ref, shallowRef } from "vue";
import HigherOrLower from "@pages/Casino/Games/HigherOrLower.vue";
import RideTheBus from "@pages/Casino/Games/RideTheBus.vue";

const { show } = useToastController()

interface Props {
  wallet: Wallet;
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
</script>

<template>
  <Head :title="$t('casino.title')" />

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
              <font-awesome-icon :icon="faWallet"/>
              {{ wallet.wallet_id.slice(0, 10) }}...
            </h4>

            <div class="d-flex gap-2">
              <BButton variant="tertiary" class="btn-square" @click="copyToClipboard()">
                <font-awesome-icon :icon="faCopy" />
              </BButton>
              <BButton variant="danger" class="btn-square" to="/casino/logout/">
                <font-awesome-icon :icon="faSignOut" />
              </BButton>
            </div>
          </template>

          <div>
            <span>
              {{ $t('casino.main.balance') }}
              <strong>{{ wallet.balance }} TJTs</strong>
            </span>

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

        <BCard class="bg-grey-100 bg-opacity-50" header-class="d-flex align-items-center justify-content-between" body-class="d-flex flex-column gap-2">
          <template #header>
            <h4 class="m-0">
              <font-awesome-icon :icon="faDice"/>
              Games
            </h4>

            <BButton variant="tertiary" class="btn-square opacity-0">
              <font-awesome-icon :icon="faCopy" />
            </BButton>
          </template>

          <BButton @click="gameComponent = HigherOrLower" :active="gameComponent === HigherOrLower">
            {{ $t('casino.game.higher_lower.title') }}
          </BButton>
          <BButton @click="gameComponent = RideTheBus" :active="gameComponent === RideTheBus">
            {{ $t('casino.game.ride_the_bus.title') }}
          </BButton>
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
</style>