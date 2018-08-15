#!/usr/bin/env python3

import datetime
import json
import logging
import pytz
import requests
import sys

from errors import SolarLogCommunicationError
from solarlog_reading import SolarLogReading


class SolarLogReader:
    def __init__(self, ip, timezone, port=80):
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)
        self.timezone = timezone
        self.address = 'http://{}:{}/getjp'.format(ip, port)

    def _attach_console_logging_handler_if_not_existing(self):
        handlers = self.logger.handlers
        handler_already_exists = any(handler.name == 'logreposit_console_handler' for handler in handlers)

        if handler_already_exists:
            return

        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.name = 'logreposit_console_handler'
        formatter = logging.Formatter('%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_live_data(self):
        live_data = self._request_live_data()
        return live_data

    def _request_live_data(self):
        live_data_request_body = {'801': {'170': None}}
        response = self._send_request(json_body=live_data_request_body)
        reading = self._parse_live_data_response(response=response)
        return reading

    def _send_request(self, json_body):
        response = requests.post(url=self.address, json=json_body)
        if response.status_code != 200:
            self.logger.error('Error communicating with SolarLog: Got response \'{}\': {}'.format(
                response.status_code, response.text))
            raise SolarLogCommunicationError()
        return response.json()

    def _parse_live_data_response(self, response):
        data = response.get('801').get('170')
        last_update_time = data.get('100')
        date = self._parse_solarlog_date(solarlog_date=last_update_time)

        reading = SolarLogReading(
            date=date,
            power_ac=data.get('101'),
            power_dc=data.get('102'),
            voltage_ac=data.get('103'),
            voltage_dc=data.get('104'),
            yield_day=data.get('105'),
            yield_yesterday=data.get('106'),
            yield_month=data.get('107'),
            yield_year=data.get('108'),
            yield_total=data.get('109'),
            consumption_power=data.get('110'),
            consumption_yield_day=data.get('111'),
            consumption_yield_yesterday=data.get('112'),
            consumption_yield_month=data.get('113'),
            consumption_yield_year=data.get('114'),
            consumption_yield_total=data.get('115'),
            total_power=data.get('116')
        )

        return reading

    def _parse_solarlog_date(self, solarlog_date):  # input looks like `15.08.18 10:58:45`
        datetime_without_timezone = datetime.datetime.strptime(solarlog_date, '%d.%m.%y %H:%M:%S')
        timezone = pytz.timezone(self.timezone)
        datetime_with_timezone = timezone.localize(datetime_without_timezone, is_dst=None)
        datetime_in_utc = datetime_with_timezone.astimezone(pytz.utc)
        return datetime_in_utc.isoformat()


def main():
    solar_log_reader = SolarLogReader(ip='10.0.0.99', timezone='Europe/Vienna')
    solar_log_reading = solar_log_reader.get_live_data()
    serialized = json.dumps(solar_log_reading.__dict__)
    print(serialized)


if __name__ == '__main__':
    main()

