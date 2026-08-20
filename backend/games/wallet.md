# Wallets

A wallet is the only account on the site. There are no passwords, no email
addresses and no user model — anyone can create one in a single click, and it is
what gates the games and r/place.

## Identity and credentials

| Field                                                    | What it is                                                                                                                                            |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `public_id`                                              | Primary key. Six characters of Crockford base32 (`0-9A-Z` without `I/L/O/U`). **Public** — shown as `Name #A1B2C3`, and stored on every r/place cell. |
| `phrase_hash`                                            | Unique, keyed hash of the wallet phrase. **The only credential.**                                                                                     |
| `legacy_id_hash`                                         | Keyed hash of the pre-phrase 32-character hex id. Good for exactly one sign-in, then `NULL`.                                                          |
| `name`, `avatar`, `balance`, `days_played`, `last_visit` | Ordinary profile and game state.                                                                                                                      |

A **wallet phrase** is six words from `wordlist.txt` (`shifter-marry-docile-…`), the
only thing a person needs to sign in. Two rules govern it:

1. **The phrase is never stored.** Only `hash_wallet_phrase()` of it — HMAC-SHA256
   keyed with `settings.WALLET_PEPPER`. A database dump alone reveals nothing.
   Changing `WALLET_PEPPER` locks every wallet out permanently.
2. **The phrase is shown exactly once**, during first-time setup, from the
   session — never from the database, because it isn't there.

Because the hash is keyed and fast, login is a single indexed lookup rather than
a scan. `normalise_wallet_phrase()` accepts any capitalisation and either spaces
or hyphens before hashing.

## `games/wallet.py` — the single entry point

Nothing outside this module should touch the session or build a query by
credential.

```python
get_wallet(request)               # the current wallet or None, cached on the request
get_wallet_by_session(session)    # same, for websockets (no request object)
set_wallet(request, wallet)       # signs in; cycles the session key
clear_wallet(request)             # signs out

create_wallet()                   # -> (wallet, phrase)   the phrase is NOT stored
find_wallet(identifier)           # by phrase
find_legacy_wallet(identifier)    # by old hex id
upgrade_legacy_wallet(wallet)     # -> phrase, and burns the legacy id
assign_wallet_phrase(wallet)      # -> phrase, replaces the current one

reveal_phrase(request, phrase, reason="registered"|"migrated")
revealable_phrase(request)        # -> {"phrase": ..., "reason": ...} or {}
phrase_is_pending(request)        # bool
stop_revealing_phrase(request)

update_balance(wallet, amount)    # ALWAYS use this for balance changes
```

`create_wallet()` returns a **tuple** — forgetting that is the easiest mistake to
make. `update_balance()` moves the same amount out of the house vault in the
opposite direction; writing `wallet.balance` directly desynchronises the vault.

Session keys: `"wallet"` holds the `public_id`, `"reveal_phrase"` holds the
pending phrase.

## Gating a view

```python
from games.decorators import wallet_required
from games.wallet import get_wallet

@wallet_required
def my_view(request):
    wallet = get_wallet(request)   # guaranteed, and already cached
```

`wallet_required` redirects to `/login/?next=<path>` when there is no wallet.
For JSON endpoints, where a redirect would arrive at the caller as a 200 with
HTML in it, use `wallet_api_required` instead — same check, but a 403 carrying
`{"error": "games.main.errors.wallet_not_found"}`.

## Routes

| Route                                | Notes                                                                        |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| `GET /login/`                        | The one sign-in page (`WalletLoginPage.vue`), site-wide, not under `/games/` |
| `POST /login/`                       | Body `{phrase, next}`. Throttled to 20 attempts per 5 minutes per address    |
| `POST /register/`                    | **POST only** — as a GET, link prefetchers created wallets                   |
| `GET /logout/`                       |                                                                              |
| `GET /games/api/user/wallet-phrase/` | `{walletPhrase, reason}`, or nulls once setup is saved                       |
| `POST /games/api/user/update/`       | `{name?, avatarId?}`; also ends the phrase reveal                            |
| `GET /games/api/user/avatars/`       | Pickable avatars                                                             |

`next` is validated by `safe_redirect()` — never redirect to an unchecked value.

## Frontend

`default_props()` puts the wallet on **every** page, so any component can read it
without a prop chain:

```json
{ "publicId", "name", "avatar", "balance", "streak", "needsSetup", "mustSavePhrase" }
```

**No credential is ever in the page props.** The phrase comes only from the
endpoint above. Keep it that way when adding fields.

`composables/wallet.ts` is a module-level store — not Pinia — that syncs itself
from the Inertia props on every navigation:

```ts
const {
  wallet,
  balance,
  balanceChange,
  isLoaded,
  openSettings,
  changeBalance,
  setName,
  setAvatar,
} = useWallet();
```

`GamesWalletSettingsModal.vue` is rendered once in `BaseLayout`, so the navbar and
the games page open the same dialog. The store opens it automatically when
`needsSetup` or `mustSavePhrase` is set, once per wallet.

For optimistic balance updates during a game, call `changeBalance(delta)`; it
also drives the `+50 / −50` flash.

## r/place

Painting requires a wallet. The consumer resolves it in `connect()` via
`get_wallet_by_session(scope["session"])` and closes the socket outright if there
is none — the page gate alone would not stop a direct websocket. `Cell.wallet` is
a `SET_NULL` FK to `public_id`, so deleting a wallet keeps the pixel and forgets
the author. Repainting a pixel in its existing colour is a no-op: nothing is
saved and nothing is broadcast.

## Admin

Wallets list at `/admin/games/wallet/`. The action **"Issue a new wallet phrase"**
generates a replacement and prints it in the admin message — the only copy, since
nothing readable is stored. The owner is not notified; pass it on by hand.

## Things that will bite you

- `create_wallet()` returns `(wallet, phrase)`, not a wallet.
- Never add the phrase or a hash to `Wallet.json()` / the page props.
- Balance changes go through `update_balance()` or the vault drifts.
- `WALLET_PEPPER` must never change on a live site.
- Migrations are excluded from ruff (`force-exclude`), so a broken migration
  passes lint — run `python -m compileall games/migrations` after editing one.
