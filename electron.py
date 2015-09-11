#!/usr/bin/env python


import Battery
import BatteryReader
import time
import sys

bat_files = [
  '/sys/class/power_supply/AC/uevent',
  '/sys/class/power_supply/BAT0/uevent',
  '/sys/class/power_supply/BAT1/uevent',
]

reader_list = []
for bf in bat_files:
  try:
    reader_list.append(BatteryReader.BatteryReader(bf))
  except:
    pass

while True:
  bat_list = []
  for reader in reader_list:
    reader.read()
    bat_list.append(reader.spawn_battery())

  for bat in bat_list:
    if bat.data.get('c_cur_now'):
      i_cur_now = bat.data.get('c_cur_now')
      i_p_now = bat.data.get('d_p_now')
      for xbat in bat_list:
        xbat.data['i_cur_now'] = i_cur_now
        xbat.data['i_p_now'] = i_p_now
        xbat.compute()
      break

  for bat in bat_list:
    sys.stdout.write('\n')
    sys.stdout.write(str(bat))
  sys.stdout.flush()

  time.sleep(3)

