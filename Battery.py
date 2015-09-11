
import copy

data_template = {
  'd_name'    : None,
  'd_online'  : None,
  'd_status'  : None,
  'd_present' : None,
  'd_v_min'   : None,
  'd_v_now'   : None,
  'd_p_now'   : None,
  'd_e_dsg'   : None,
  'd_e_max'   : None,
  'd_e_now'   : None,
  'd_ch_dsg'  : None,
  'd_ch_max'  : None,
  'd_ch_now'  : None,
  'd_cur_now' : None,
  'd_cap_now' : None,

  'd_tech': None,
  'd_cycle': None,
  'd_capacity': None,
  'd_model': None,
  'd_manufacturer': None,
  'd_serial': None,

  'c_e_per'   : None,
  'c_cur_now' : None,
  'c_t_chr_left'  : None,
  'c_t_dis_chr_left'  : None,

  'i_cur_now' : None, # inject values from other sources to provide approximations
  'i_p_now' : None,
}

parse_mapping = {
  'POWER_SUPPLY_NAME': 'd_name',
  'POWER_SUPPLY_ONLINE': 'd_online',
  'POWER_SUPPLY_STATUS': 'd_status',
  'POWER_SUPPLY_PRESENT': 'd_present',
  'POWER_SUPPLY_VOLTAGE_MIN_DESIGN': 'd_v_min',
  'POWER_SUPPLY_VOLTAGE_NOW': 'd_v_now',
  'POWER_SUPPLY_POWER_NOW': 'd_p_now',
  'POWER_SUPPLY_ENERGY_FULL_DESIGN': 'd_e_dsg',
  'POWER_SUPPLY_ENERGY_FULL': 'd_e_max',
  'POWER_SUPPLY_ENERGY_NOW': 'd_e_now',
  'POWER_SUPPLY_CHARGE_FULL_DESIGN': 'd_ch_dsg',
  'POWER_SUPPLY_CHARGE_FULL': 'd_ch_max',
  'POWER_SUPPLY_CHARGE_NOW': 'd_ch_now',
  'POWER_SUPPLY_CURRENT_NOW': 'd_cur_now',
  'POWER_SUPPLY_CAPACITY': 'd_cap_now',
  'POWER_SUPPLY_TECHNOLOGY': 'd_tech',
  'POWER_SUPPLY_CYCLE_COUNT': 'd_cycle',
  'POWER_SUPPLY_CAPACITY_LEVEL': 'd_capacity',
  'POWER_SUPPLY_MODEL_NAME': 'd_model',
  'POWER_SUPPLY_MANUFACTURER': 'd_manufacturer',
  'POWER_SUPPLY_SERIAL_NUMBER': 'd_serial',

}

u_coef = 1000000

compute_set = {
  'c_e_per'   : [ 
    lambda x: x['d_e_now']/x['d_e_max']*100,  
    lambda x: x['d_ch_now']/x['d_ch_max']*100,  
  ],
  'c_cur_now' : [
    lambda x: x['d_p_now']/x['d_v_now']*1000,
  ],
  'c_t_chr_left'  : [
    lambda x: (x['d_e_max']-x['d_e_now'])/x['i_p_now'],
    lambda x: (x['d_ch_max']-x['d_ch_now'])/x['i_cur_now'],
    lambda x: (x['d_e_max']-x['d_e_now'])/x['d_p_now'],
    lambda x: (x['d_ch_max']-x['d_ch_now'])/x['d_cur_now'],
  ],  
  'c_t_dis_chr_left'  : [
    lambda x: x['d_e_now']/x['i_p_now'],
    lambda x: x['d_ch_now']/x['i_cur_now'],
    lambda x: x['d_e_now']/x['d_p_now'],
    lambda x: x['d_ch_now']/x['d_cur_now'],
  ],
}

state_sign_table = {
  'Full': '[ ]',
  'Unknown': '[ ]',
  'Charging': '[+]',
  'Discharging': '[-]',
  '1': '(+)',
  '0': '( )'
}

def time2str(time_str):
  tmf = float(time_str)
  hours = int(tmf)
  tmf = (tmf - int(tmf)) * 60
  minutes = int(tmf)
  return "%d:%02d" % (hours, minutes)



class Battery:
  def __init__(self, origin):
    self.origin = origin
    self.parse()
    self.compute()

  def __str__(self):
    name = self.data.get('d_name')
    icon = state_sign_table[self.data.get('d_status')]
    energy = "%.1f%%" % (self.data.get('c_e_per'))

    time = ''
    if self.data.get('c_t_dis_chr_left'):
      time = time2str(self.data.get('c_t_dis_chr_left'))
    elif self.data.get('c_t_chr_left'):
      time = time2str(self.data.get('c_t_chr_left'))
   
    current = ''
    if self.is_charging():
      current = "+%dmAh" % (self.data.get('c_cur_now'))
    if self.is_discharging():
      current = "-%dmAh" % (self.data.get('c_cur_now'))

    tmp = ' '.join([name, icon, energy, time, current])

    return tmp

  def get_state(self):
    return self.data.get('d_status')

  def is_charging(self):
    return self.get_state() == 'Charging'

  def is_discharging(self):
    return self.get_state() == 'Discharging'

  def is_ac(self):
    return self.data.get('d_name') == 'AC'

  def parse(self):
    self.data = copy.copy(data_template)

    for line in self.origin:
      try:
        key, value = line.strip().split('=')
        self.data[parse_mapping[key]] = value
        self.data[parse_mapping[key]] = float(value)
      except Exception, exc:
        pass

  def compute(self):
    if self.is_ac():
      return
    for c_key, c_flist in compute_set.iteritems():
      for c_func in c_flist:
        try:
          self.data[c_key] = c_func(self.data)
        except Exception, exc:
          pass


class Ac(Battery):
  def __str__(self):
    name = self.data.get('d_name')
    icon = state_sign_table[str(int(self.data.get('d_online')))]
    tmp = ' '.join([name, icon])
    return tmp

