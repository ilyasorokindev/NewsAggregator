# AGENTS.md — News Aggregator Frontend

Guide for AI coding agents working in this repository.

---

## What This Project Is

A React + TypeScript SPA that provides two pages:

1. **Search** — user enters a query, the app calls the backend and displays matching news chunks as cards.
2. **Settings** — user manages the list of news source websites (CRUD); the backend scrapes those URLs.

The frontend does **not** crawl, scrape, embed, or interact with the vector database. All communication is through the REST API exposed by the backend (`BE_CC/`).

---

## Running Locally

**Prerequisites:** Node.js 18+, npm.

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Type-check + build
npm run build
```

Backend must be running at `http://localhost:8000` (see `BE_CC/AGENTS.md`).

---

## Tech Stack

| Tool | Version | Role |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 5.7 | Type safety (strict mode) |
| Redux Toolkit | 2 | Global state management |
| React Router | 7 | Client-side routing |
| Material UI (MUI) | 6 | Component library and styling |
| Axios | 1 | HTTP client |
| Vite | 6 | Build tool and dev server |

---

## Architecture

Feature-based structure. Every feature owns its own API layer, components, pages, Redux slice, thunks, and types. Shared infrastructure lives in `src/shared/`.

```
src/
  app/
    store.ts          # Redux store root
    router.tsx        # React Router config
    hooks.ts          # Typed useAppDispatch / useAppSelector

  shared/
    api/
      httpClient.ts          # Axios instance (baseURL from env or localhost:8000)
      getApiErrorMessage.ts  # Extracts error.detail from backend responses
    components/
      layout/
        AppLayout.tsx        # Top nav bar + navigation links + <Outlet>
    types/
      index.ts               # Shared TypeScript types

  features/
    search/
      api/searchApi.ts               # GET /search?s=query
      components/
        SearchForm.tsx               # Query input + submit button
        SearchResults.tsx            # Renders list of cards or empty/error state
        SearchResultCard.tsx         # Single result card (displays text, hides guid)
      pages/SearchPage.tsx           # Composes search UI
      store/
        searchSlice.ts               # SearchState: results, loading, error
        searchThunks.ts              # searchNews(query) async thunk
      types.ts                       # SearchResult { guid, text }

    settings/
      api/settingsApi.ts             # GET /setup/items, POST/PUT/DELETE /setup/item
      components/
        WebsiteList.tsx              # Renders list of items + Add button
        WebsiteItem.tsx              # Single row with Edit / Delete actions
        WebsiteDialog.tsx            # Add / Edit dialog with URL field
        DeleteWebsiteDialog.tsx      # Confirmation dialog before deletion
      pages/SettingsPage.tsx         # Composes settings UI
      store/
        settingsSlice.ts             # SettingsState: items, loading, error
        settingsThunks.ts            # loadWebsites, createWebsite, updateWebsite, deleteWebsite
      types.ts                       # WebsiteItem { guid, url }
      utils/urlValidation.ts         # URL format validation helper

  main.tsx            # Entry point — mounts <Provider> + <RouterProvider>
```

---

## Redux State Shape

```typescript
// Root state
{
  search: SearchState,
  settings: SettingsState
}

// SearchState
{
  results: SearchResult[],  // [{ guid, text }]
  loading: boolean,
  error: string | null
}

// SettingsState
{
  items: WebsiteItem[],     // [{ guid, url }]
  loading: boolean,
  error: string | null
}
```

---

## API Summary

Backend base URL: `http://localhost:8000`

| Method | Path | Description |
|---|---|---|
| GET | `/search?s={query}` | Search news; returns `[{ guid, text }]` |
| GET | `/setup/items` | List all source websites; returns `[{ guid, url }]` |
| POST | `/setup/item` | Add source `{ url }` |
| PUT | `/setup/item` | Update source `{ guid, url }` |
| DELETE | `/setup/item` | Delete source `{ guid }` |

All errors from the backend return `{ "detail": "..." }`. Use `getApiErrorMessage` from `shared/api/getApiErrorMessage.ts` to extract the user-facing message.

---

## Code Guidelines

### TypeScript

- Strict mode is on. Never use `any`.
- Use explicit interfaces and types. Types live in `types.ts` within each feature.

### Components

- Functional components only — no class components.
- One responsibility per component; keep components under 200 lines.
- Props must be explicitly typed.
- Use named exports: `export const SearchPage = () => {}` — avoid default exports.
- PascalCase for component names and files.

### Naming

| Kind | Convention | Example |
|---|---|---|
| Components | PascalCase | `SearchResults.tsx` |
| Functions / variables | camelCase | `loadWebsites` |
| Constants | UPPER_SNAKE_CASE | `BASE_URL` |

### Imports

Order: React → third-party → shared → feature → relative.

### Styling

- Use MUI components (`Stack`, `Box`, `Grid`, `Paper`, `Typography`, etc.).
- Prefer the `sx` prop for one-off styles.
- Avoid custom CSS files.

### State Management

- All global state lives in Redux; never use Context API for app state.
- Use `createSlice` and `createAsyncThunk` from Redux Toolkit.
- Do not use redux-thunk manually, redux-saga, or MobX.
- Create selectors for all state access — components must not reach into deep state manually.

### API / Data Flow

```
UI → dispatch thunk → API service (features/*/api) → backend → Redux store → UI
```

- Components **never** call Axios directly.
- All HTTP calls go through the centralized `httpClient` in `shared/api/httpClient.ts`.
- No duplicate request code.

### Error Handling

Every async thunk must handle `pending / fulfilled / rejected`. Loading, success, and error states must be explicitly represented in the slice.

---

## What to Avoid

- Business logic inside components — put it in thunks or services.
- Direct API calls from components — all calls go through `features/*/api`.
- Using `any` anywhere in TypeScript.
- Adding global mutable state outside Redux.
- Using Context API for application-level state.
- Custom CSS files when MUI `sx` works.
- Default exports from component or page files.
