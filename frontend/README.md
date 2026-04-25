# Research Agent — Frontend (Phase 4)

Next.js 14 App Router UI for the multi-agent research pipeline with HITL review.

## Stack

| Layer | Choice |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS |
| Markdown | `react-markdown` + `rehype-highlight` |
| Icons | Inline SVG (zero dependency) |
| Types | Full TypeScript |

---

## Quick Start

```bash
# 1. Install deps
npm install

# 2. Set backend URL
cp .env.local.example .env.local
# edit NEXT_PUBLIC_API_URL if backend isn't on :8000

# 3. Run dev server
npm run dev
# → http://localhost:3000
```

---

## Project Structure

```
app/
  layout.tsx                  # Root layout — nav + fonts
  page.tsx                    # Home: research form + hero
  not-found.tsx               # 404 page
  research/
    [id]/
      page.tsx                # Job status + AgentTrace polling
      loading.tsx             # Skeleton while server-fetching
      review/
        page.tsx              # HITL review screen

components/
  ResearchForm.tsx            # Question input + submit
  AgentTrace.tsx              # Step cards + 2s polling loop
  HITLPanel.tsx               # Flagged claims + feedback + approve/reject
  ReportViewer.tsx            # Markdown report with copy button
  StatusBadge.tsx             # Color-coded job status pill

lib/
  api.ts                      # Typed API client (all endpoint functions)

types/
  css.d.ts                    # CSS module declarations
```

---

## API Contract

The frontend expects these endpoints on `NEXT_PUBLIC_API_URL`:

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/research/start` | Start a job → `{ id }` |
| `GET` | `/api/research/:id/status` | Poll status + steps |
| `GET` | `/api/research/:id` | Full job + report |
| `POST` | `/api/research/:id/approve` | Submit HITL decision |

See `lib/api.ts` for full request/response shapes.

---

## User Journey

```
/ (Home)
  └─ ResearchForm submits question
       └─ POST /api/research/start → redirects to /research/:id

/research/:id
  └─ AgentTrace polls every 2s
       ├─ status: running    → shows step cards updating live
       ├─ status: awaiting_review → banner + auto-redirect to /review
       └─ status: complete   → renders ReportViewer

/research/:id/review
  └─ HITLPanel shows flagged claims + summaries
       ├─ "Approve & Continue" → POST approve → back to /research/:id
       └─ "Reject & Refine"   → POST reject  → back to /research/:id
```

---

## Key Implementation Details

### Polling (`AgentTrace.tsx`)
- `useEffect` + `setInterval` at 2000ms
- Clears interval on terminal states (`complete`, `failed`, `awaiting_review`)
- On `awaiting_review`: 800ms delay then `router.push` to review screen
- Error state shown inline; polling continues on transient errors

### Typed API Client (`lib/api.ts`)
- Single `apiFetch` wrapper handles status codes + error parsing
- `ApiError` class carries HTTP status for downstream handling
- All endpoint functions are individually exported + documented

### Markdown Rendering (`ReportViewer.tsx`)
- `react-markdown` with `rehype-highlight` for syntax highlighting
- `github-dark` highlight.js theme, overridden to match dark bg
- Custom `.prose-research` CSS class for typography
- Word count + estimated read time in header

### Server vs Client Split
- `app/research/[id]/page.tsx` — **Server Component**: fetches initial state, passes to client
- `AgentTrace.tsx` — **Client Component**: owns polling lifecycle
- `HITLPanel.tsx` — **Client Component**: owns form state + API calls
- `ResearchForm.tsx` — **Client Component**: owns input + navigation

---

## Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000   # Backend base URL (no trailing slash)
```
