<script setup lang="ts">
import LeaderboardPosition from "@/components/Quiz/LeaderboardPosition.vue";
import { QuizPlayer } from "@/types/Quiz/QuizPlayer";
import { ref } from "vue";

interface LeaderboardScreenProps {
  players: QuizPlayer[];
}

const { players } = defineProps<LeaderboardScreenProps>();
const listOfPlayers = ref<QuizPlayer[]>([]);

listOfPlayers.value = [...players];

function shuffle() {
  listOfPlayers.value.forEach((player) => {
    const delta = Math.floor(Math.random() * 50) + 1; // +1 bis +50
    player.addScore(delta);
  });

  sort();
}

function sort() {
  requestAnimationFrame(() => {
    listOfPlayers.value.sort((a, b) => b.score - a.score);
  });
}

function remove(item: QuizPlayer) {
  const i = listOfPlayers.value.indexOf(item);
  if (i > -1) {
    listOfPlayers.value.splice(i, 1);
  }
}
</script>

<template>
  <div
    class="d-flex flex-column gap-3 col-12 col-md-8 col-lg-6 inner-screen overflow-hidden overflow-y-auto"
  >
    <span class="fs-1 fw-bold text-center">Leaderboard</span>

    <div class="d-flex flex-column gap-2">
      <TransitionGroup
        tag="div"
        name="leaderboard-fade"
        class="d-flex flex-column gap-2 position-relative"
      >
        <LeaderboardPosition
          v-for="player in listOfPlayers"
          :key="player.id"
          :name="player.name"
          :score="player.score"
          @click="remove(player)"
          :url="player.image"
        />
      </TransitionGroup>
    </div>

    <div class="d-flex justify-content-evenly gap-2">
      <BButton @click="shuffle">Shuffle</BButton>
    </div>
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

.inner-screen {
  max-height: 100%;
}
</style>
