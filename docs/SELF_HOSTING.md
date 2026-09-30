# Run the API in Docker (no cloud payment needed)

Render's free plan is 0.1 CPU / 512 MB and sleeps after 15 minutes. Docker on your own
computer uses that computer's CPU and RAM instead (any normal laptop is many times faster).
The website stays on Vercel and the database on Supabase (both free).

## 1. Start the API
```
cp backend/.env.example backend/.env      # fill in GROQ_API_KEYS / GEMINI_API_KEYS, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
docker compose up -d --build              # first build takes several minutes (downloads the search model)
curl http://localhost:8000/api/health     # {"ok":true,"index_ready":true}
```
Uses about 400 MB of RAM. `restart: unless-stopped` brings it back after a reboot.

## 2. Give it a public HTTPS address (free, no domain, no card)
Vercel's website has to reach your computer, so publish port 8000 through a tunnel. Tailscale
Funnel gives a stable address (`https://<computer>.<tailnet>.ts.net`); check Tailscale's current
free-plan terms before relying on it:
```
tailscale funnel 8000
```
(Cloudflare quick tunnels and ngrok's free static domain also work; a URL that changes on every
restart will break the site, so use a stable one.)

## 3. Point the website at it
- Vercel → Project → Settings → Environment Variables: set `NEXT_PUBLIC_API_URL` to the tunnel
  address, then redeploy (the browser security policy is built from this value at build time).
- In `backend/.env` set `CORS_ORIGINS=https://kanooni-sathi.vercel.app`, then
  `docker compose up -d`.

## Trade-offs
- The computer must stay on and online 24/7. Power or internet cuts take the API down; Render
  free is the fallback (leave it deployed, switch `NEXT_PUBLIC_API_URL` back).
- Keep the computer updated and never open router ports; the tunnel needs none.
- Later, move the same image to a Nepal VPS you can pay for in NPR: `docker compose up -d`.
