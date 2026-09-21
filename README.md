# Nearby Watch — Hyperlocal Lost & Found / Community Alert Board

A hyperlocal board for lost pets, lost/found items, and neighborhood safety
alerts. Post something, see what's nearby on a map, and get a live
notification when something new shows up within range of you.

## Stack

| Layer | Choice |
|---|---|
| Backend | FastAPI, MongoDB (Beanie ODM over Motor) |
| Auth | JWT (access + refresh), bcrypt password hashing, email OTP verification |
| Real-time | Native FastAPI WebSockets, in-memory connection manager |
| Frontend | React (Vite), React Router, Tailwind CSS, Leaflet / OpenStreetMap |
| File storage | Local disk (dev), abstracted behind a swappable interface |

## Quick start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `MONGO_URI` to a MongoDB Atlas free-tier cluster
connection string (Atlas is recommended over a local MongoDB install — same
connection string works locally and once deployed).

```bash
python -m app.seed     # optional: creates ~15 demo posts so the map isn't empty
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`, interactive docs at
`http://localhost:8000/docs`.

**Important:** open `app/seed.py` and change `CENTER_LAT` / `CENTER_LNG` to
your own city before seeding, or the demo posts will show up around Mumbai.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env      # defaults already point at localhost:8000
npm run dev
```

Open `http://localhost:5173`.

### 3. Try it

1. Register an account (check your **backend terminal** for the OTP code —
   the default `console` email provider logs it there instead of sending a
   real email, so nothing to configure to try this out).
2. Verify, then browse the map — you'll see the seeded demo posts.
3. Create a post; other logged-in users within `NOTIFY_RADIUS_KM` (default
   5km) get a live toast notification via WebSocket, plus a persisted
   notification in their Alerts tab.

## Architecture notes

### Geospatial queries
Posts store `location` as a GeoJSON `Point`, indexed with a MongoDB
`2dsphere` index. The nearby-posts endpoint uses `$near` with `$maxDistance`
— MongoDB does the distance filtering and sorting server-side, no manual
Haversine math needed for the query itself (a separate Haversine helper
*is* used for the WebSocket proximity check, since that happens in memory
against currently-connected sockets, not against the database).

> **Note on this delivery:** I validated the full request flow (auth, OTP,
> posts, comments, notifications, permissions, and the live WebSocket push)
> end-to-end using an in-memory mock MongoDB — see `backend/tests/smoke_test.py`.
> That mock doesn't implement the `$near` operator, so the geospatial query
> itself is standard, well-documented MongoDB syntax but **hasn't been
> exercised against a real MongoDB engine**. Run the smoke test's manual
> equivalent (create two posts at different distances, query `/api/posts/nearby`)
> against your real Atlas cluster once you're set up, to confirm before you
> build further on top of it.

### Real-time notifications
WebSocket connections are held in an in-memory `dict` on the server
(`app/services/ws_manager.py`), not Redis. This is a deliberate MVP choice:
Redis pub/sub is only needed once you run multiple server processes (so a
notification triggered on worker A reaches a client connected to worker B).
For local dev and a single-instance deployment, one process handles
everything. The dispatch logic is isolated in its own module specifically so
swapping in Redis later — if you ever run `uvicorn --workers 4` or deploy
across multiple instances — is a contained change, not a rewrite.

### OTP handling
OTP codes are hashed (SHA-256) before storage — never stored in plaintext,
not even in the database. A MongoDB **TTL index** on `expires_at`
(`expireAfterSeconds=0`) automatically deletes expired OTP documents; there's
no cleanup cron job or background worker needed.

### Email delivery
`app/services/email/` defines a provider-agnostic interface. The active
provider is chosen at runtime via `EMAIL_PROVIDER` in `.env`:
- `console` (default) — logs the code to the terminal, zero setup
- `resend` / `sendgrid` — real adapters, activate by adding the matching API
  key

### File storage
`app/services/storage.py` is the single interface post-creation code calls
(`save_file` / `delete_file`). It currently writes to local disk
(`uploads/posts/`), but the rest of the app never touches the filesystem
directly — swapping to S3 or Cloudinary later means changing what happens
inside those two functions, not the endpoints that call them.

## Project structure

```
backend/
  app/
    models/         Beanie documents (User, Post, Comment, Notification, OtpVerification)
    schemas/         Pydantic request/response models
    core/            security.py (JWT, bcrypt), deps.py (auth dependency)
    services/
      email/         provider-agnostic email adapter (console/resend/sendgrid)
      otp_service.py OTP generation, hashing, cooldown, attempt-limiting
      storage.py      local file storage, swappable backend
      ws_manager.py   in-memory WebSocket connection manager
    routers/          auth, posts, comments, notifications, websocket
    main.py           FastAPI app, CORS, static file mount, route registration
    seed.py           demo data script
  tests/
    smoke_test.py     end-to-end flow test against an in-memory mock Mongo

frontend/
  src/
    api/              axios client (with JWT refresh interceptor) + endpoint wrappers
    context/           AuthContext, NotificationContext (WebSocket + toasts + unread badge)
    components/        Navbar, PostCard, MapView, ProtectedRoute, ToastStack
    pages/              Home (map/list), CreatePost, PostDetail, MyPosts, Notifications, auth pages
```
