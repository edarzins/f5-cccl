#!/usr/bin/env python
# Copyright 2017 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from mock import MagicMock
import pytest

import f5_cccl.resource.ltm.monitor.udp_monitor as target


@pytest.fixture
def udp_config():
    return {"name": "test_monitor",
            "partition": "Test",
            "interval": 1,
            "timeout": 10,
            "send": "GET /\r\n",
            "recv": "SERVER"}


@pytest.fixture
def bigip():
    bigip = MagicMock()
    return bigip


def test_create_w_defaults(udp_config):
    monitor = target.UDPMonitor(
        name=udp_config['name'],
        partition=udp_config['partition'])

    assert monitor
    assert monitor.name == "test_monitor"
    assert monitor.partition == "Test"
    data = monitor.data
    assert data.get('interval') == 5
    assert data.get('timeout') == 16
    assert data.get('send') == ""
    assert data.get('recv') == ""

def test_create_w_config(udp_config):
    monitor = target.UDPMonitor(
        **udp_config
    )

    assert monitor
    assert monitor.name == "test_monitor"
    assert monitor.partition == "Test"
    data = monitor.data
    assert data.get('interval') == 1
    assert data.get('timeout') == 10
    assert data.get('send') == "GET /\r\n"
    assert data.get('recv') == "SERVER"


def test_get_uri_path(bigip, udp_config):
    monitor = target.UDPMonitor(**udp_config)

    assert (monitor._uri_path(bigip) ==
            bigip.tm.ltm.monitor.udps.udp)


def test_create_icr_monitor(udp_config):
    monitor = target.IcrUDPMonitor(**udp_config)

    assert isinstance(monitor, target.UDPMonitor)


def test_create_api_monitor(udp_config):
    monitor = target.ApiUDPMonitor(**udp_config)

    assert isinstance(monitor, target.UDPMonitor)


def test_create_monitors_invalid(udp_config):
    # Set interval to be larger than timeout,
    # ICR Monior will be created, API Monitor will not
    udp_config['interval'] = 30
    monitor = target.IcrUDPMonitor(**udp_config)

    assert isinstance(monitor, target.IcrUDPMonitor)

    with pytest.raises(ValueError):
        monitor = target.ApiUDPMonitor(**udp_config)
