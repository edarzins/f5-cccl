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

from f5_cccl.resource.ltm.virtual import VirtualServer
from f5_cccl.resource.ltm.pool import Pool
from mock import Mock
import pytest


cfg_minimal = {'destination': '1.2.3.4', 'servicePort': 80}


@pytest.fixture
def bigip():
    bigip = Mock()
    return bigip


def test_create_virtual_min_config():
    """Test of Virtual Server create without name or port."""
    partition = 'Common'
    name = 'virtual_1'

    virtual = VirtualServer(
        name=name,
        partition=partition,
        **cfg_minimal
    )
    assert virtual

    # verify all cfg items
    for k,v in cfg_minimal.items():
        assert virtual.data[k] == v


'''
def test_create_virtual_invalid():
    """Test of Virtual Server create without name or port."""
    partition = 'Common'
    name = 'virtual_1'
    cfg = {'destination': '1.2.3.4', 'servicePort': 80}


    with pytest.raises(TypeError):
        virtual = VirtualServer(
            name=None,
            partition=partition,
            **cfg
        )
        assert not virtual
'''


def test_hash():
    partition = 'Common'
    name = 'virtual_1'
    cfg = {'destination': '1.2.3.4', 'servicePort': 80}

    virtual = VirtualServer(
        name=name,
        partition=partition,
        **cfg_minimal
    )
    virtual1 = VirtualServer(
        name=name,
        partition=partition,
        **cfg_minimal
    )
    virtual2 = VirtualServer(
        name='test',
        partition=partition,
        **cfg_minimal
    )
    virtual3 = VirtualServer(
        name=name,
        partition='other',
        **cfg_minimal
    )

    assert hash(virtual) == hash(virtual1)
    assert hash(virtual) != hash(virtual2)
    assert hash(virtual) != hash(virtual3)


def test_eq():
    partition = 'Common'
    name = 'virtual_1'
    cfg = {'destination': '1.2.3.4', 'servicePort': 80}

    virtual = VirtualServer(
        name=name,
        partition=partition,
        **cfg_minimal
    )
    virtual2 = VirtualServer(
        name=name,
        partition=partition,
        **cfg_minimal
    )
    pool = Pool(
        name=name,
        partition=partition
    )
    assert virtual
    assert virtual2
    assert virtual == virtual2

    # not equal
    virtual2.data['servicePort'] = 8080
    assert virtual != virtual2

    # different objects
    with pytest.raises(ValueError):
        assert virtual != pool 


def test_uri_path(bigip):
    partition = 'Common'
    name = 'virtual_1'
    virtual = VirtualServer(
        name=name,
        partition=partition,
        **cfg_minimal
    )

    assert virtual._uri_path(bigip) == bigip.tm.ltm.virtuals.virtual
