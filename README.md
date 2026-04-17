Get species_dashboard here: https://github.com/vkberndt/species_dashboard_public
(I forgot I already had a "species_dashboard" repo for my private version. So just follow all the same steps but with "species_dashboard_public" instead of just "species_dashboard")

# Species Dashboard Deployment Guide

No coding knowledge required. Follow each step in order.

---

## How it works

```
Game Server (Path of Titans)
        │
        │  HTTP POST (PlayerRespawn event logs)
        ▼
  Webhook Service
  (Railway)        - Receives the event, parses it, saves it to the database
        │
        ▼
  PostgreSQL Database
  (Railway)
        │
        ▼
  Dashboard Website
  (Railway)        - Shows species login stats, charts, leaderboards etc
```

---

## What you need before starting

- A free [Railway](https://railway.app) account

---

## Step 1 - Create a Railway project

1. Go to [railway.app](https://railway.app) and log in
2. Click **New Project** → **Empty Project**
3. Give it a name like `species-tracker`

---

## Step 2 - Add a Postgres database

1. Inside your Railway project, click **+ Add a Service**
2. Choose **Database** → **PostgreSQL**
3. Wait until the status shows **Active**

---

## Step 3 - Set up your database tables

1. Click on your Postgres service → **Database** tab
2. Open `schema.sql` in Notepad or any text editor
3. Copy the entire contents and paste into the Railway query box (Under "Data" and already has the start of a * SELECT..... query)
4. Press enter to **Run Query**. You should see no errors

---

## Step 4 - Deploy the webhook service

This is the service your game server will send events to.

1. Click **+ Add** → **GitHub Repo** → select `species-webhook`

**Connect it to your database:**
1. Click the webhook service → **Variables** tab
2. Click **+ Add Variable Reference**
3. Select your Postgres service → select `DATABASE_URL`
4. Deploy

**Get your webhook URL:**
1. Click the species-webhook deployment box → **Settings** → **Networking** → **Generate Domain**
2. Copy the domain — it will look like: `species-webhook-production-xxxx.up.railway.app`

---

## Step 5 — Point your game server at the webhook

Open your server's `Game.ini` and update the `[ServerWebhooks]` section:

```ini
[ServerWebhooks]
bEnabled=true
PlayerRespawn="https://YOUR-DOMAIN.up.railway.app/pot/PlayerRespawn"
```

Save and restart your game server.

---

## Step 6 — Verify events are coming in

1. Click on your webhook service → **Logs** tab
2. Have a player spawn in on your server
3. You should see this in the logs within a few seconds:

```
--------------------------------------------------
  ► Event received: PlayerRespawn
  ► Time: 2024-01-15 14:32:01
  ► Player ID:  12345-ABCDE
  ► Species:    Triceratops
  ✔ Saved to database: player 12345-ABCDE spawned as Triceratops
--------------------------------------------------
```

If you see the `✔ Saved to database` line, everything is working.

---

## Step 7 — Deploy the dashboard

1. Click **+ Add a Service** → **GitHub Repo** → select `species-dashboard`
2. Click **Deploy** and wait for the green checkmark

**Connect it to your database:**
1. Click the dashboard service → **Variables** tab
2. Click **+ Add Variable Reference**
3. Select your Postgres service → select `DATABASE_URL`

**Get your dashboard URL:**
1. Click the dashboard service → **Settings** → **Networking** → **Generate Domain**
2. Open that URL in your browser — your dashboard is live!

---

## Troubleshooting

**Health check URL shows an error**
- Check the **Logs** tab on the webhook service
- Make sure `DATABASE_URL` was added as a variable reference in Step 4

**Logs show no events after a player respawns**
- Double-check the URL in `Game.ini` matches your Railway domain exactly
- Make sure `bEnabled=true` is set and the game server was restarted

**Dashboard shows "No data yet"**
- Confirm the webhook is receiving events first (Step 6)
- Make sure you ran `schema.sql` in Step 3

**Any other errors**
- The **Logs** tab on each service will show exactly what went wrong
