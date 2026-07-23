# H-014C.1 — Authentication initialization note

## Question

Was a deterministic race causing protected property requests before auth
initialization (transient 401 during Habitat smoke)?

## Trace

| Layer | Behavior |
|-------|----------|
| Token storage | HttpOnly `access_token` cookie — not a frontend bearer |
| Init | `AuthContext` `GET /auth/me` on mount; `user` starts `null` |
| Route guards | `Protected` waits while `user === null`; redirects when `user === false` |
| Data loading | `AppDataContext` `enabled: !!user` / `!!pid` |
| Twin / reality | `ExistingRoomTwinPanel` waits for `user !== null` before fetch |

## Result

**No reproducible defect requiring a code fix beyond the existing gates.**

Anonymous `/auth/me` → 401 is normal and clears to `user = false`. Invalid or
expired cookies still yield genuine 401s. Demo configuration does not alter
authentication. Artificial sleeps / hard-coded tokens / broad retry loops /
auth bypasses were **not** introduced.
