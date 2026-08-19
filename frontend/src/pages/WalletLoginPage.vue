<script setup lang="ts">
import { Head, router } from "@inertiajs/vue3";
import { computed, reactive, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";

interface WalletLoginPageProps {
  error: string | null;
  /** Where to land once a wallet is active. */
  next: string;
}

const { error, next } = defineProps<WalletLoginPageProps>();

const i18n = useI18n();
const { create } = useToast();

watch(
  () => error,
  (newError) => {
    if (!newError) return;

    create({
      body: i18n.t(newError),
      variant: "danger",
      position: "bottom-start",
    });
  },
);

const registerUrl = computed(
  () => `/register/?next=${encodeURIComponent(next)}`,
);

const form = reactive({
  walletId: null as string | null,
});

const validateWalletId = computed(() => {
  if (form.walletId === null) return null;

  return /^[0-9a-f]{32}$/i.test(form.walletId);
});

function submit() {
  router.post("/login/", { ...form, next });
}
</script>

<template>
  <Head :title="$t('games.entry.title')" />

  <div class="container-fixed flex flex-col items-center justify-center">
    <UiAlert variant="danger">
      <vue-markdown :source="$t('games.entry.warning')" />
    </UiAlert>

    <div class="w-full shrink-0 sm:w-1/2 md:w-5/12 lg:w-1/3 xl:w-1/4">
      <UiCard body-class="flex flex-col gap-4">
        <template #header>
          <h1 class="m-0 text-center">
            <iconify-icon icon="fa-solid:wallet" />
            {{ $t("games.entry.title") }}
          </h1>
        </template>

        <UiButton variant="primary" class="w-full" :to="registerUrl">
          {{ $t("games.entry.enter_with_new_wallet") }}
        </UiButton>

        <div class="flex items-center gap-2 text-accent">
          <hr class="grow border-light/25" />
          {{ $t("games.login.or") }}
          <hr class="grow border-light/25" />
        </div>

        <form @submit.prevent="submit" class="flex w-full flex-col gap-2">
          <UiFormGroup
            id="wallet-id-group"
            label-for="wallet-id-input"
            :label="$t('games.login.title')"
          >
            <UiInput
              id="wallet-id-input"
              v-model="form.walletId"
              :placeholder="$t('games.login.enter_wallet')"
              required
              :state="validateWalletId"
              type="password"
            />
            <UiInvalidFeedback :state="validateWalletId">
              {{ $t("games.login.error.not_valid") }}
            </UiInvalidFeedback>
          </UiFormGroup>

          <UiButton
            type="submit"
            variant="secondary"
            class="w-full"
            :disabled="!validateWalletId"
          >
            {{ $t("games.login.submit") }}
          </UiButton>
        </form>
      </UiCard>
    </div>
  </div>
</template>
