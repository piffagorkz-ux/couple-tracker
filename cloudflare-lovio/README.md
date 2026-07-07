# Lovio Cloudflare Edition

This is a standalone Cloudflare rewrite that lives alongside the current Flask/Render app.

## Stack

- Cloudflare Workers (native JavaScript worker)
- Cloudflare D1
- Static frontend from `public/`

## Why this version exists

The original app is a server-rendered Flask application for Render. This version is rebuilt natively for Cloudflare so the app can wake instantly and feel faster on mobile.

I chose a native Worker rewrite instead of Cloudflare Python Workers because the current Cloudflare docs still list Python Workers as beta, while a standard Worker path is the safer production target for this app shape.

## Included in this first rewrite

- Registration and login
- Partner invitations
- Daily question with mood slider and answer reveal after both partners answer
- Daily activity rotation with 6 choices and 7-day cooldown
- Goals
- Date plans with accept/decline and 24-hour expiry after acceptance
- Wishes
- Important dates
- Russian / English interface switch
- Gender-based accent theme

## Local setup

1. Open this folder:
   - `cloudflare-lovio`
2. Install dependencies:
   - `npm install`
3. Create a D1 database:
   - `npx wrangler d1 create lovio-db`
4. Put the returned `database_id` into `wrangler.toml`.
5. Run the schema:
   - `npx wrangler d1 execute lovio-db --local --file=./schema.sql`
6. Start dev:
   - `npm run dev`

## Deploy

1. Run the schema in production:
   - `npx wrangler d1 execute lovio-db --remote --file=./schema.sql`
2. Deploy:
   - `npm run deploy`

## Notes

- This rewrite is intentionally separate from the Flask app so Render can stay online.
- D1 is SQLite-based, so migration from Postgres data would need a one-time import script later.
- This is the first Cloudflare edition, not a pixel-perfect clone of every Flask screen yet.
