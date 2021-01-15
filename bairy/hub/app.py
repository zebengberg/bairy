"""FastAPI app to display device data."""

import json
from multiprocessing import Process
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
from bairy.hub.configs import LOG_PATH
from bairy.hub.request import get_all_statuses, run_requests
from bairy.hub.dash_plot import dash_plot
from bairy.hub.request import validate_names
from bairy import device


device.utils.print_local_ip_address()
device.app.configure_app_logging(LOG_PATH)
app = FastAPI()
app.mount('/plot', WSGIMiddleware(dash_plot.server))


@app.get('/')
async def root():
  """Redirect to docs."""
  return RedirectResponse(url='/docs')


@app.get('/status', response_class=PlainTextResponse)
async def status():
  """Get status of each device."""
  statuses = get_all_statuses()
  return json.dumps(statuses, indent=4)


@app.get('/logs', response_class=PlainTextResponse)
async def logs():
  """Return app log as plain text."""
  with open(LOG_PATH) as f:
    return f.read()


def run_app():
  """Run app as separate process."""
  uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
  validate_names()
  p = Process(target=run_app)
  p.start()
  run_requests()
