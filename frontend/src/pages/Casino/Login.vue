<script setup lang="ts">
import { Head, router } from "@inertiajs/vue3";
import { faDice } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { computed, reactive } from "vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController";
import {useI18n} from "vue-i18n";
import { watch } from "vue";

interface Props {
  error: undefined | string;
}

const i18n = useI18n();
const { create } = useToastController()

const { error } = defineProps<Props>();

watch(() => error, (newError) => {
  if (newError) {
    create?.({
      props: {
        body: i18n.t(newError),
        variant: "danger",
        interval: 5000,
        position: "bottom-start",
      }
    });
  }
});

const form = reactive({
  walletId: null
})

function submit() {
  router.post('/casino/login/', form)
}

const validateWalletId = computed(() => {
  if (form.walletId === null) {
    return null;
  }

  const uuidRegex = /^[0-9a-f]{32}$/i;
  return uuidRegex.test(form.walletId);
});
</script>

<template>
  <Head :title="$t('casino.title')" />

  <div class="container text-white d-flex flex-column align-items-center justify-content-center">
    <BAlert :model-value="true" variant="danger">
      <vue-markdown :source="$t('casino.entry.warning')" />
    </BAlert>

    <div class="col-12 col-sm-6 col-md-5 col-lg-4 col-xl-3">
      <BCard class="bg-grey-100 bg-opacity-50" body-class="d-flex flex-column align-items-center gap-2">
        <template #header>
          <h1 class="text-center">
            <font-awesome-icon :icon="faDice"/>
            {{ $t('casino.login.title') }}
          </h1>
        </template>

        <BForm @submit.prevent="submit" class="d-flex flex-column gap-2 w-100">
          <BFormGroup id="input-group-2" label-for="input-2">
            <BFormInput id="input-2" v-model="form.walletId" :placeholder="$t('casino.login.enter_wallet')" required :state="validateWalletId" type="password" />
            <BFormInvalidFeedback :state="validateWalletId">
              {{ $t('casino.login.error.not_valid') }}
            </BFormInvalidFeedback>
          </BFormGroup>

          <BButton type="submit" variant="primary" class="w-100" :disabled="!validateWalletId">{{ $t('casino.login.submit') }}</BButton>
        </BForm>

        <BLink to="/casino/">
          {{ $t('casino.login.back_to_entry') }}
        </BLink>
      </BCard>
    </div>
  </div>

  <BToastOrchestrator />
</template>