import type { Avatar } from "@/types/Avatar.ts";

export interface Wallet {
  /** Public, non-secret discriminator: two players may share a name. */
  publicId: string;
  name: string;
  balance: number;
  streak: number;
  avatar: Avatar | null;
  /** Still on the default name and/or without an avatar. */
  needsSetup: boolean;
  /** A freshly issued phrase is waiting to be written down. */
  mustSavePhrase: boolean;
}
