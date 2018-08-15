#!/usr/bin/env python3

import json
import logging
import os
import requests
import sys
import time
import traceback

from errors import ConfigurationError
from solarlog_reader import SolarLogReader

DEVICE_TOKEN_ENV_VAR_NAME = 'DEVICE_TOKEN'
API_BASE_URL_ENV_VAR_NAME = 'API_BASE_URL'
SOLARLOG_IP_ADDRESS_ENV_VAR_NAME = 'SOLARLOG_IP'
SOLARLOG_PORT_ENV_VAR_NAME = 'SOLARLOG_PORT'
SOLARLOG_TIMEZONE = 'SOLARLOG_TIMEZONE'
READ_INTERVAL_ENV_VAR_NAME = 'READ_INTERVAL'
API_BASE_URL_DEFAULT_VALUE = 'https://api.logreposit.com/v1/'
SOLARLOG_PORT_DEFAULT_VALUE = "80"
READ_INTERVAL_DEFAULT_VALUE = "30000"


class SolarLogReaderService:
    def __init__(self, device_token, api_base_url, solarlog_ip, solarlog_timezone, interval, solarlog_port):
        self.logger = self._set_up_logger()
        self.device_token = device_token
        self.api_base_url = api_base_url
        self.solarlog_ip = solarlog_ip
        self.solarlog_port = solarlog_port
        self.solarlog_timezone = solarlog_timezone
        self.interval = interval
        self.solarlog_reader = SolarLogReader(ip=solarlog_ip, timezone=solarlog_timezone, port=solarlog_port)

    def _set_up_logger(self):
        logger = logging.getLogger('SolarLogReaderService')
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.name = 'logreposit_console_handler'
        formatter = logging.Formatter('%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def run(self):
        self._check_required_arguments()

        while True:
            try:
                self._retrieve_and_publish_values()
            except:
                msg = traceback.format_exc()
                self.logger.error('Caught exception: {}'.format(msg))

            time.sleep(self.interval / 1000)

    def _check_required_arguments(self):
        if self.device_token is None:
            self.logger.error('{} environment variable is not set.'.format(DEVICE_TOKEN_ENV_VAR_NAME))
            raise ConfigurationError()
        if self.api_base_url is None:
            self.logger.error('{} environment variable is not set.'.format(API_BASE_URL_ENV_VAR_NAME))
            raise ConfigurationError()
        if self.solarlog_ip is None:
            self.logger.error('{} environment variable is not set.'.format(SOLARLOG_IP_ADDRESS_ENV_VAR_NAME))
            raise ConfigurationError()
        if self.solarlog_port is None:
            self.logger.error('{} environment variable is not set.'.format(SOLARLOG_PORT_ENV_VAR_NAME))
            raise ConfigurationError()
        if self.solarlog_timezone is None:
            self.logger.error('{} environment variable is not set.'.format(SOLARLOG_TIMEZONE))
            raise ConfigurationError()
        if self.interval is None:
            self.logger.error('{} environment variable is not set.'.format(READ_INTERVAL_ENV_VAR_NAME))
            raise ConfigurationError()

    def _retrieve_and_publish_values(self):
        reading = self.solarlog_reader.get_live_data()
        self.logger.info(reading.__dict__)
        self._publish_values(reading=reading)

    def _publish_values(self, reading):
        self.logger.info('Publishing values ...')

        url = self.api_base_url + 'ingress'
        headers = {
            'x-device-token': self.device_token
        }
        data = {
            'deviceType': 'SOLARLOG',
            'data': reading.__dict__
        }

        self.logger.info('Publishing values to {}: {}'.format(url, json.dumps(data)))
        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 202:
            self.logger.error('Got HTTP status code \'{}\': {}'.format(response.status_code, response.text))
        else:
            self.logger.info('Successfully published data.')


def main():
    device_token = os.getenv(DEVICE_TOKEN_ENV_VAR_NAME, None)
    api_base_url = os.getenv(API_BASE_URL_ENV_VAR_NAME, API_BASE_URL_DEFAULT_VALUE)
    solarlog_ip = os.getenv(SOLARLOG_IP_ADDRESS_ENV_VAR_NAME, None)
    solarlog_timezone = os.getenv(SOLARLOG_TIMEZONE, None)
    solarlog_port = os.getenv(SOLARLOG_PORT_ENV_VAR_NAME, SOLARLOG_PORT_DEFAULT_VALUE)
    read_interval = os.getenv(READ_INTERVAL_ENV_VAR_NAME, READ_INTERVAL_DEFAULT_VALUE)

    if solarlog_port is not None:
        solarlog_port = int(solarlog_port)

    if read_interval is not None:
        read_interval = int(read_interval)

    solar_log_reader_service = SolarLogReaderService(
        device_token=device_token,
        api_base_url=api_base_url,
        solarlog_ip=solarlog_ip,
        solarlog_port=solarlog_port,
        solarlog_timezone=solarlog_timezone,
        interval=read_interval
    )

    solar_log_reader_service.run()


if __name__ == '__main__':
    main()
