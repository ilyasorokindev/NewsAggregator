# CLAUDE.md — News Aggregator Frontend

## Project

React 19 + TypeScript SPA. Two pages: **Search** (semantic news search via vector backend) and **Settings** (CRUD for news source URLs). No crawling, scraping, or embedding — frontend communicates exclusively through the REST API at `http://localhost:8000`.

Full spec: `.cursor/rules/`. Full agent guide: `AGENTS.md`.

---

## Commands

```bash
npm run dev      # dev server → http://localhost:5173
npm run build    # tsc + vite build
```

---

## Architecture Rules

**Feature-based structure.** Every feature (`search`, `settings`) owns its own:
`api/` → `components/` → `pages/` → `store/` → `types.ts`

**Data flow — never break this:**
```
UI → dispatch thunk → features/*/api → httpClient → backend → Redux store → UI
```

- Components **never** call Axios or fetch directly.
- All HTTP calls go through `shared/api/httpClient.ts`.
- All global state lives in Redux Toolkit. Context API is forbidden for app state.
- No business logic in components — thunks only.

---

## Code Rules

- **TypeScript strict** — never use `any`.
- **Named exports only** — no default exports from components or pages.
- **Functional components only** — no class components, no hooks outside components/custom hooks.
- **MUI + `sx` prop** — no custom CSS files.
- Every async thunk must handle `pending / fulfilled / rejected` states in the slice.
- Use `getApiErrorMessage` from `shared/api/getApiErrorMessage.ts` to extract backend error messages (`{ detail: "..." }`).

---

## State Shape

```typescript
{ search: { results, loading, error }, settings: { items, loading, error } }
```

---

## API Endpoints

| Method | Path | Notes |
|---|---|---|
| GET | `/search?s={query}` | Returns `[{ guid, text }]` |
| GET | `/setup/items` | Returns `[{ guid, url }]` |
| POST | `/setup/item` | Body: `{ url }` |
| PUT | `/setup/item` | Body: `{ guid, url }` |
| DELETE | `/setup/item` | Body: `{ guid }` |

---

## Do Not

- Use `any` in TypeScript.
- Call Axios from a component.
- Use Context API for application state.
- Add default exports.
- Add custom CSS files when MUI `sx` works.
- Put business logic inside components.
