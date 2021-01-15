"""FastAPI app to display device data."""

import json
from multiprocessing import Process
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
from starlette.middleware.wsgi import WSGIMiddleware
from bairy.hub.configs import load_ips
from bairy.hub.request import get_size, get_configs, get_name, run_request
from bairy.hub.dash_plot import dash_plot
from bairy.hub.request import validate_names


app = FastAPI()
app.mount('/plot', WSGIMiddleware(dash_plot.server))


@app.get('/')
async def root():
  """Get details of each devices."""
  ip_addresses = load_ips()
  configs = [await get_configs(ip_address) for ip_address in ip_addresses]
  sizes = [await get_size(ip_address) for ip_address in ip_addresses]
  for c, s in zip(configs, sizes):
    c['size'] = s
  return configs


@app.get('/names')
async def names():
  """Get names of each devices."""
  ip_addresses = load_ips()
  return [await get_name(ip_address) for ip_address in ip_addresses]


@app.get('/pretty', response_class=PlainTextResponse)
async def pretty():
  """Pretty print root()."""
  configs = await root()
  return json.dumps(configs, indent=4)


def run_app():
  """Run app as separate process."""
  uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
  validate_names()
  p = Process(target=run_app)
  p.start()
  run_request()
