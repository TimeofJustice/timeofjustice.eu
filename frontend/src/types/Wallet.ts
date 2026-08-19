import type { Avatar } from "@/types/Avatar.ts";

export interface Wallet {
  name: string;
  walletId: string;
  balance: number;
  streak: number;
  avatar: Avatar | null;
}
