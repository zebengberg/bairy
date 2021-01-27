"""FastAPI app to display device data."""

import json
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
from bairy.hub import configs
from bairy.hub.request import get_all_statuses
from bairy.hub.dash_plot import dash_plot
from bairy import log_configs


app = FastAPI()
app.mount('/plot', WSGIMiddleware(dash_plot.server))


@app.get('/')
def root():
  """Redirect to plot."""
  return RedirectResponse(url='/plot')


@app.get('/status', response_class=PlainTextResponse)
def status():
  """Get status of each device."""
  statuses = get_all_statuses()
  return json.dumps(statuses, indent=4)


@app.get('/logs', response_class=PlainTextResponse)
def logs():
  """Return app log as plain text."""
  with open(configs.LOG_PATH) as f:
    return f.read()


def run_app():
  """Run app as separate process."""
  uvicorn.run(
      app,
      host='0.0.0.0',
      port=8000,
      log_config=log_configs.get_uvicorn_logger(configs.LOG_PATH)
  )
