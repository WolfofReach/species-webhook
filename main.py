import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import psycopg2
import psycopg2.pool
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

DATABASE_URL = os.environ["DATABASE_URL"]
pool = psycopg2.pool.ThreadedConnectionPool(2, 10, DATABASE_URL)

print("=" * 50)
print("  Webhook service starting up...")
print("  Listening for game events.")
print("=" * 50)


def log_species_event(aid: str, species: str, event_type: str = "PlayerRespawn"):
    ts = datetime.now(timezone.utc)
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO public.species_logins (ts, aid, species, event_type)
                   VALUES (%s, %s, %s, %s)""",
                (ts, aid, species, event_type),
            )
        conn.commit()
        print(f"  ✔ Saved to database: player {aid} spawned as {species}")
    except Exception as e:
        conn.rollback()
        print(f"  ✘ Database error for player {aid}: {e}")
    finally:
        pool.putconn(conn)


@app.route("/pot/<event_name>", methods=["POST"])
def handle_event(event_name):
    data = request.get_json(silent=True, force=True) or {}

    print("-" * 50)
    print(f"  ► Event received: {event_name}")
    print(f"  ► Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if event_name == "PlayerRespawn":
        try:
            desc = data["embeds"][0]["description"]
            details = {}
            for line in desc.splitlines():
                clean = line.strip().replace("**", "")
                if ": " in clean:
                    k, v = clean.split(": ", 1)
                    details[k] = v

            dino = details.get("DinosaurType")
            aid = details.get("PlayerAlderonId")

            if dino and aid:
                print(f"  ► Player ID:  {aid}")
                print(f"  ► Species:    {dino}")
                log_species_event(aid, dino)
            else:
                print(f"  Could not find DinosaurType or PlayerAlderonId in payload.")
                print(f"  Raw details parsed: {details}")

        except Exception as e:
            print(f"  Failed to parse PlayerRespawn payload: {e}")
            print(f"  Raw data received: {json.dumps(data)}")
    else:
        print(f"  No action configured for '{event_name}' — event acknowledged.")

    print("-" * 50)
    return jsonify({"status": "ok", "event": event_name}), 200


@app.route("/health", methods=["GET"])
def health():
    """Simple health check — open this URL in a browser to confirm the service is live."""
    return jsonify({
        "status": "online",
        "message": "Webhook service is running and ready to receive events."
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
