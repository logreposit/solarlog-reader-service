class SolarLogReading:
    def __init__(self,
                 date,
                 power_ac,
                 power_dc,
                 voltage_ac,
                 voltage_dc,
                 yield_day,
                 yield_yesterday,
                 yield_month,
                 yield_year,
                 yield_total,
                 consumption_power,
                 consumption_yield_day,
                 consumption_yield_yesterday,
                 consumption_yield_month,
                 consumption_yield_year,
                 consumption_yield_total,
                 total_power):
        self.date = date
        self.powerAc = power_ac
        self.powerDc = power_dc
        self.voltageAc = voltage_ac
        self.voltageDc = voltage_dc
        self.yieldDay = yield_day
        self.yieldYesterday = yield_yesterday
        self.yieldMonth = yield_month
        self.yieldYear = yield_year
        self.yieldTotal = yield_total
        self.consumptionPower = consumption_power
        self.consumptionYieldDay = consumption_yield_day
        self.consumptionYieldYesterday = consumption_yield_yesterday
        self.consumptionYieldMonth = consumption_yield_month
        self.consumptionYieldYear = consumption_yield_year
        self.consumptionYieldTotal = consumption_yield_total
        self.totalPower = total_power
