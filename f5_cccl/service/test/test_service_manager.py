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

import json
import pickle
import pytest
from f5_cccl.test.conftest import big_ip

from f5_cccl.api import F5CloudServiceManager
from f5_cccl.bigip import CommonBigIP
from f5_cccl.resource import ltm

from f5_cccl.service.manager import ServiceConfigDeployer
from f5_cccl.service.config_reader import ServiceConfigReader

from mock import MagicMock
from mock import Mock
from mock import patch

@pytest.fixture
def service_manager():
    bigip = MagicMock()
    partition = "Test"

    service_mgr = F5CloudServiceManager(
        bigip,
        partition)

    return service_mgr


def xtest_apply_config(service_manager):
    services = {}

    assert service_manager.apply_config(services)


class TestServiceConfigDeployer:

    def setup(self):
        self.bigip = big_ip()
        self.partition = "Test"

        svcfile = 'f5_cccl/schemas/tests/service.json'
        with open(svcfile, 'r') as fp:
            self.service = json.loads(fp.read())

        config_reader = ServiceConfigReader(self.partition)
        self.desired_config = config_reader.read_config(self.service)

    def test_create_deployer(self):
        deployer = ServiceConfigDeployer(
            self.bigip)

        assert deployer

    def test_deploy(self):

        deployer = ServiceConfigDeployer(
            self.bigip)

        assert 0 == deployer.deploy(self.desired_config)

    def test_delete_nodes(self):
        deployer = ServiceConfigDeployer(self.bigip)

        # mock the call to _delete_resources and then check that the args
        # are correct
        deployer._delete_resources = Mock()

        deployer._cleanup_nodes()

        assert deployer._delete_resources.called
        assert 1 == deployer._delete_resources.call_count
        assert 2 == len(deployer._delete_resources.call_args[0][0])
        nodes = deployer._delete_resources.call_args[0][0]
        expected_set = set(['10.2.3.4', '10.2.3.5%0'])
        for node in nodes:
            assert node.name in expected_set