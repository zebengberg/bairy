from itertools import count


class DataSource:
  _id = count(0)

  def __init__(self, url, name, location):
    self.id = None
    self.url = url
    self.name = name
    self.location = location
