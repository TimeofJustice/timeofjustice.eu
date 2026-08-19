import { computed, reactive, readonly, ref, watch } from "vue";
import { usePage } from "@inertiajs/vue3";
import axios from "axios";
import type { Avatar } from "@/types/Avatar.ts";
import type { Wallet } from "@/types/Wallet.ts";

const wallet = reactive<Wallet>({
  name: "",
  walletId: "",
  balance: 0,
  streak: 0,
  avatar: null,
});

const loaded = ref(false);

/** Last balance delta, kept around briefly so the UI can animate it. */
const balanceChange = ref(0);
let balanceChangeTimeout: ReturnType<typeof setTimeout> | undefined;

const setWallet = (newWallet: Wallet) => {
  Object.assign(wallet, newWallet);
  loaded.value = true;
};

const clearWallet = () => {
  Object.assign(wallet, {
    name: "",
    walletId: "",
    balance: 0,
    streak: 0,
    avatar: null,
  });
  loaded.value = false;
};

const setName = (name: string) => {
  wallet.name = name;
};

const setAvatar = (avatar: Avatar | null) => {
  wallet.avatar = avatar;
};

/** Copies the wallet id. The caller reports success or failure. */
const copyWalletId = () => navigator.clipboard.writeText(wallet.walletId);

/**
 * Shared with the settings modal, which `BaseLayout` renders once so the games
 * page and the navbar open the same dialog. The wallet badge sits in three
 * navbar slots, so the open state cannot live in it.
 */
const settingsOpen = ref(false);

const openSettings = () => {
  settingsOpen.value = true;
};

const avatars = ref<Avatar[]>([]);
let avatarRequest: Promise<void> | null = null;

/** Fetches the pickable avatars once and reuses them for later openings. */
const loadAvatars = () => {
  avatarRequest ??= axios
    .get("/games/api/user/avatars/")
    .then((response) => {
      avatars.value = response.data.avatars;
    })
    .catch((error) => {
      // Let the next opening try again rather than showing an empty grid forever.
      avatarRequest = null;
      throw error;
    });

  return avatarRequest;
};

/** Adds `tokens` to the balance and exposes the delta via `balanceChange`. */
const changeBalance = (tokens: number, duration = 1000) => {
  wallet.balance += tokens;
  balanceChange.value = tokens;

  clearTimeout(balanceChangeTimeout);
  balanceChangeTimeout = setTimeout(() => {
    balanceChange.value = 0;
  }, duration);
};

const setBalance = (balance: number) => {
  wallet.balance = balance;
};

let syncing = false;

/**
 * `default_props` shares the wallet on every page, so the store can keep itself
 * in sync with the server on each navigation. Local changes made while playing
 * survive until the next response overwrites them.
 *
 * Started on first use rather than at import time, so `usePage()` is always
 * called after Inertia has initialised.
 */
const startSync = () => {
  if (syncing) return;
  syncing = true;

  const page = usePage();

  watch(
    () => page.props?.wallet as Wallet | null | undefined,
    (incoming) => (incoming ? setWallet(incoming) : clearWallet()),
    { immediate: true },
  );
};

/**
 * Global games wallet, available on every page. Seeded from the shared Inertia
 * props, so components read it straight from here instead of having the wallet
 * threaded through props.
 */
export const useWallet = () => {
  startSync();

  return {
    wallet: readonly(wallet),
    isLoaded: readonly(loaded),
    balance: computed(() => wallet.balance),
    balanceChange: readonly(balanceChange),
    setWallet,
    clearWallet,
    setName,
    setAvatar,
    copyWalletId,
    settingsOpen,
    openSettings,
    avatars: readonly(avatars),
    loadAvatars,
    setBalance,
    changeBalance,
  };
};
