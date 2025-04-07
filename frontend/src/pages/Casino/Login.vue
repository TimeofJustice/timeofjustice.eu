<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import { faDice } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { ref } from "vue";
import { useToastController } from "@node_modules/bootstrap-vue-next/dist/src/composables/useToastController";

interface Props {
  error: undefined | string;
}

const { error } = defineProps<Props>();

const text = ref<string>('');
const { show } = useToastController()

if (error) {
  show?.({
    props: {
      title: "Error",
      body: error,
      variant: "danger",
      interval: 5000,
      pos: "bottom-start",
    }
  });
}
</script>

<template>
  <Head :title="$t('casino.title')" />

  <div class="container text-white d-flex flex-column align-items-center justify-content-center">
    <div>
      <BCard class="bg-grey-100 bg-opacity-50">
        <BCardHeader>
          <h1 class="text-center">
            <font-awesome-icon :icon="faDice"/>
            {{ $t('casino.entry') }}
          </h1>
        </BCardHeader>
        <BCardBody class="d-flex flex-column align-items-center">
          <div class="d-flex flex-column align-items-center gap-2">
            <BFormInput v-model="text" placeholder="Enter your name" />
            <BButton variant="secondary" class="w-100" to="/casino/?wallet=Test">
              {{ $t('casino.entry.already_own_wallet') }}
            </BButton>
          </div>
        </BCardBody>
      </BCard>
    </div>
  </div>

  <BToastOrchestrator />
</template>