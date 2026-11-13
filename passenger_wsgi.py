"""cPanel (Passenger) entry point for the OutboundAI dashboard.

cPanel's "Setup Python App" only speaks WSGI, but server.py is FastAPI (ASGI).
a2wsgi bridges the two. Passenger also doesn't fire FastAPI startup events,
so we run that startup code ourselves once at import time.

If packages aren't installed yet (or the app fails to load), we serve a plain
error page instead of crashing, so cPanel's "Run Pip Install" check still passes.
"""
import os
import sys
import traceback

APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)                 # so load_dotenv(".env") and ui/ paths resolve
sys.path.insert(0, APP_DIR)
os.environ.setdefault("TZ", "UTC")

try:
    import asyncio
    import threading
    from a2wsgi import ASGIMiddleware
    from server import app, _startup  # noqa: E402

    _loop = asyncio.new_event_loop()
    threading.Thread(target=_loop.run_forever, daemon=True).start()

    # run the FastAPI startup hook (creates default users, starts scheduler)
    try:
        asyncio.run_coroutine_threadsafe(_startup(), _loop).result(timeout=60)
    except Exception as e:  # don't crash the whole site if Supabase is slow
        print("startup hook failed:", e, file=sys.stderr)

    application = ASGIMiddleware(app, loop=_loop)

except Exception:
    _err = traceback.format_exc()
    print(_err, file=sys.stderr)

    def application(environ, start_response):
        body = ("App is not ready yet (packages missing or load error).\n\n" + _err).encode()
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
