"""Launch uvicorn server and process requests with FastAPI."""

import random
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


class Data(BaseModel):
  index: list[int]


app = FastAPI()


@app.get('/')
async def root():
  """Get most recent data point."""
  return random.random()


@app.get('/data/')
async def data():
  """Get all data not previously checked in."""
  return {'hello': random.random()}


@app.post('/received/')
async def received(d: Data):
  """Post a check-in."""
  print(d)


if __name__ == '__main__':
  # uvicorn.run(app)
  uvicorn.run('server:app', reload=True)
