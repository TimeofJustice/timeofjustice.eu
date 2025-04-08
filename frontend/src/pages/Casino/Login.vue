<script setup lang="ts">
import { Head, router } from "@inertiajs/vue3";
import { faDice } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { computed, reactive } from "vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController";
import {useI18n} from "vue-i18n";

interface Props {
  error: undefined | string;
}

const { error } = defineProps<Props>();

const i18n = useI18n();

const { show } = useToastController()

const form = reactive({
  wallet_id: null
})

function onSubmit() {
  router.post('/casino/login/', form)
}

import { watch } from "vue";

watch(() => error, (newError) => {
  if (newError) {
    show?.({
      props: {
        body: i18n.t(newError),
        variant: "danger",
        interval: 5000,
        pos: "bottom-start",
      }
    });
  }
});

const validation = computed(() => {
  if (form.wallet_id === null) {
    return null;
  }

  const uuidRegex = /^[0-9a-f]{32}$/i;
  return uuidRegex.test(form.wallet_id);
});
</script>

<template>
  <Head :title="$t('casino.title')" />

  <div class="container text-white d-flex flex-column align-items-center justify-content-center">
    <div class="col-3">
      <BCard class="bg-grey-100 bg-opacity-50" body-class="d-flex flex-column align-items-center gap-2">
        <template #header>
          <h1 class="text-center">
            <font-awesome-icon :icon="faDice"/>
            {{ $t('casino.login.title') }}
          </h1>
        </template>

        <BForm @submit.prevent="onSubmit" class="d-flex flex-column gap-2 w-100">
          <BFormGroup id="input-group-2" label-for="input-2">
            <BFormInput id="input-2" v-model="form.wallet_id" :placeholder="$t('casino.login.enter_wallet')" required :state="validation" />
            <BFormInvalidFeedback :state="validation">
              {{ $t('casino.login.error.not_valid') }}
            </BFormInvalidFeedback>
          </BFormGroup>

          <BButton type="submit" variant="primary" class="w-100">{{ $t('casino.login.submit') }}</BButton>
        </BForm>

        <BLink to="/casino/">
          {{ $t('casino.login.back_to_entry') }}
        </BLink>
      </BCard>
    </div>
  </div>

  <BToastOrchestrator />
</template>