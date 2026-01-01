<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { BAvatar } from "bootstrap-vue-next";
import { ref } from "vue";

import LeaderboardPosition from "./LeaderboardPosition.vue";

interface Position {
  id: number;
  name: string;
  score: number;
}

const items = ref<Position[]>([
  { id: 0, name: "Alice", score: 0 },
  { id: 1, name: "Bob", score: 0 },
]);
let nextId = 2;

function insert() {
  items.value.splice(items.value.length, 0, {
    id: nextId++,
    name: "Test",
    score: 0,
  });
  resyncGifs();
}

function shuffle() {
  items.value.forEach((item) => {
    const delta = Math.floor(Math.random() * 50) + 1; // +1 bis +50
    item.score += delta;
  });

  requestAnimationFrame(() => {
    items.value.sort((a, b) => b.score - a.score);
  });
}

function remove(item: Position) {
  const i = items.value.indexOf(item);
  if (i > -1) {
    items.value.splice(i, 1);
  }
}

const gifSyncKey = ref(Date.now());

function resyncGifs() {
  gifSyncKey.value = Date.now();
}

const showLeaderboard = ref(false);

function toggleLeaderboard() {
  showLeaderboard.value = !showLeaderboard.value;
}
</script>

<template>
  <Head :title="$t('quiz.title')" />

  <BButton class="container-xxl" @click="toggleLeaderboard">
    Leaderboard anzeigen
  </BButton>

  <div
    class="container-xxl flex-grow-1 overflow-x-hidden d-flex justify-content-center position-relative"
  >
    <Transition name="fade">
      <div
        class="d-flex flex-column justify-content-center gap-2 col-6 position-absolute h-100"
        v-if="!showLeaderboard"
      >
        <BCard class="mb-2" variant="secondary">
          Ich stelle dir die Frage des Lebens? Ich stelle dir die Frage des
          Lebens? Ich stelle dir die Frage des Lebens?
        </BCard>
        <BCard>
          Ich bin eine Antwort, oder vielleicht doch zwei

          <div class="position-absolute top-0 w-100 translate-middle-y pe-4">
            <BAvatarGroup
              size="2.3rem"
              overlap="0.4"
              class="reverse hover-focus"
            >
              <BAvatar class="p-0 border border-2 border-black">
                <span class="b-avatar-img position-absolute">
                  <img
                    :src="`https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTA2NnF5YWViY25sdDJhb3Q2OTVrdzNmY2ptNnI3YTl2N3Fta2NvaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Dg4TxjYikCpiGd7tYs/giphy.gif?t=${gifSyncKey}`"
                  />
                </span>
              </BAvatar>
            </BAvatarGroup>
          </div>
        </BCard>
        <BCard>
          Ich bin eine Antwort, oder vielleicht doch zwei

          <div class="position-absolute top-0 w-100 translate-middle-y pe-4">
            <BAvatarGroup
              size="2.3rem"
              overlap="0.4"
              class="reverse hover-focus"
            >
              <BAvatar text="+4" class="p-0 border border-2 border-black" />
              <BAvatar class="p-0 border border-2 border-black">
                <span class="b-avatar-img position-absolute">
                  <img src="https://i.imgur.com/lkWFHkU.gif" />
                </span>
              </BAvatar>
              <BAvatar class="p-0 border border-2 border-black">
                <span class="b-avatar-img position-absolute">
                  <img
                    :src="`https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTA2NnF5YWViY25sdDJhb3Q2OTVrdzNmY2ptNnI3YTl2N3Fta2NvaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Dg4TxjYikCpiGd7tYs/giphy.gif?t=${gifSyncKey}`"
                  />
                </span>
              </BAvatar>
              <BAvatar class="p-0 border border-2 border-black">
                <span class="b-avatar-img position-absolute">
                  <img
                    :src="`https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZjZydWhxdmZqZWtjendmNDZnNHg4bHdlcTdrNG43N3RvYWVoa3pqYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/NsKiCmWdA96V4w10N5/giphy.gif?t=${gifSyncKey}`"
                  />
                </span>
              </BAvatar>
              <BAvatar class="p-0 border border-2 border-black">
                <span class="b-avatar-img position-absolute">
                  <img
                    :src="`https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif?t=${gifSyncKey}`"
                  />
                </span>
              </BAvatar>
              <BAvatar class="p-0 border border-2 border-black">
                <span class="b-avatar-img position-absolute">
                  <img
                    :src="`https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif?t=${gifSyncKey}`"
                  />
                </span>
              </BAvatar>
            </BAvatarGroup>
          </div>
        </BCard>
        <BCard variant="success">
          Ich bin eine Antwort, oder vielleicht doch zwei

          <div class="position-absolute top-0 w-100 translate-middle-y pe-4">
            <BAvatarGroup
              size="2.3rem"
              overlap="0.4"
              class="reverse hover-focus"
            >
            </BAvatarGroup>
          </div>
        </BCard>
        <BCard>
          Ich bin eine Antwort, oder vielleicht doch zwei

          <div class="position-absolute top-0 w-100 translate-middle-y pe-4">
            <BAvatarGroup
              size="2.3rem"
              overlap="0.4"
              class="reverse hover-focus"
            >
              <BAvatar class="p-0 border border-2 border-black">
                <span class="b-avatar-img position-absolute">
                  <img
                    :src="`https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif?t=${gifSyncKey}`"
                  />
                </span>
              </BAvatar>
            </BAvatarGroup>
          </div>
        </BCard>
      </div>

      <div
        class="d-flex flex-column justify-content-center gap-2 col-4 position-absolute h-100"
        v-else-if="showLeaderboard"
      >
        <span class="fs-1 fw-bold text-center">Leaderboard</span>

        <div class="d-flex flex-column align-items-stretch gap-2">
          <BButton @click="insert">Add</BButton>
          <BButton @click="shuffle">Shuffle</BButton>
        </div>

        <div class="d-flex flex-column gap-2">
          <TransitionGroup
            tag="div"
            name="leaderboard-fade"
            class="d-flex flex-column gap-2 position-relative"
          >
            <LeaderboardPosition
              v-for="item in items"
              :key="item.id"
              :name="item.name"
              :score="item.score"
              @click="remove(item)"
              :url="`https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif?t=${gifSyncKey}`"
            />
          </TransitionGroup>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped lang="scss">
.leaderboard-fade-move,
.leaderboard-fade-enter-active,
.leaderboard-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

.leaderboard-fade-enter-from,
.leaderboard-fade-leave-to {
  opacity: 0;
  margin-bottom: -0.5rem;
}

.leaderboard-fade-enter-from {
  transform: translateX(-50px);
}

.leaderboard-fade-leave-to {
  transform: translateX(50px);
}

.leaderboard-fade-leave-active {
  height: 0%;
  width: 100%;
}

/* Fade für Umschalten zwischen Frage & Leaderboard */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.4s ease,
    transform 0.4s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}
</style>
