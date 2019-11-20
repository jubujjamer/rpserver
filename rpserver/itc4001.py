from lantz import Feat, DictFeat, Action
from lantz import Q_
from lantz.drivers.thorlabs import ITC4020
from lantz.errors import InstrumentError
from lantz.messagebased import MessageBasedDriver

from time import sleep

if __name__ == '__main__':
    import logging
    import sys
    from lantz.log import log_to_screen
    log_to_screen(logging.CRITICAL)
    res_name = "USB0::0x1313::0x804A::M00404162::INSTR"
    on_time = 10
    fmt_str = "{:<30}|{:>30}"
    with ITC4020(res_name) as inst:
        inst.pulse_mode = 'QCW'
        print(inst.pulse_mode)
        print(fmt_str.format("Temperature unit", inst.temperature_unit))
        print(fmt_str.format("Device name", inst.query('*IDN?')))
        print(fmt_str.format("LD state", inst.ld_state))
        print(fmt_str.format("TEC state", inst.tec_state))
        print(fmt_str.format("LD current ", inst.ld_current_setpoint))
        inst.ld_current = Q_(0.1, 'A')
        print(fmt_str.format("LD current ", inst.ld_current_setpoint))
        print("Turning on TEC and LD...")
        inst.tec_state = True
        sleep(4)
        inst.ld_state = True
        sleep(4)
        inst.ld_current = Q_(0.15, 'A')
        print(fmt_str.format("LD current ", inst.ld_current))
        sleep(1)
        inst.ld_current = Q_(0.1, 'A')
        sleep(4)
        print(fmt_str.format("LD power (via photodiode)", inst.ld_power['pd']))
        print(fmt_str.format("LD current ", inst.ld_current))
        sleep(on_time)
        print("Turning off TEC and LD...")
        inst.tec_state = False
        inst.ld_state = False
        print(fmt_str.format("LD state", inst.ld_state))
        print(fmt_str.format("TEC state", inst.tec_state))
