
import Battery

class BatteryReader:
  def __init__(self, filename):
    self.filename = filename
    self.fh = None
    self.data = None
    self.reset()
    self.read()

  def __del__(self):
    self.fh.close()

  def __str__(self):
    tmp = "BatteryReader ( %s, %s )" % ( self.filename, not self.fh.closed )
    return tmp

  def reset(self):
    if self.fh and not self.fh.closed():
      self.fh.close()
    self.fh = open(self.filename, 'r')

  def clear(self):
    self.data = None

  def read(self):
    self.clear()
    self.fh.seek(0)
    self.data = self.fh.readlines()
    return self.data

  def get_printable_data(self):
    tmp = ''.join(self.data)
    return tmp

  def spawn_battery(self):
    tmp = Battery.Battery(self.data)
    if tmp.is_ac():
      tmp = Battery.Ac(self.data)
    return tmp
