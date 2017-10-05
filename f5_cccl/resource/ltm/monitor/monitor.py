"""Hosts an interface for the BIG-IP Monitor Resource.

This module references and holds items relevant to the orchestration of the F5
BIG-IP for purposes of abstracting the F5-SDK library.
"""
#
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

import logging

from f5_cccl.resource import Resource


LOGGER = logging.getLogger(__name__)


class Monitor(Resource):
    """Creates a CCCL BIG-IP Monitor Object of sub-type of Resource.

    This object hosts the ability to orchestrate basic CRUD actions against a
    BIG-IP Monitor via the F5-SDK.
    """

    properties = dict(timeout=16, interval=5)

    def __eq__(self, compare):
        """Check the equality of the two objects.

        Do a straight data-to-data comparison.
        """
        myself = self._data

        if isinstance(compare, Monitor):
            compare = compare.data

        return myself == compare

    def __init__(self, name, partition, **kwargs):
        """Initialize the Monitor object."""
        super(Monitor, self).__init__(name, partition)

        for key, value in self.properties.items():
            self._data[key] = kwargs.get(key, value)

    def __str__(self):
        """Generate a string representation of the object."""
        return("Monitor(partition: {}, name: {}, type: {})".format(
            self._data['partition'], self._data['name'], type(self)))

    def _uri_path(self, bigip):
        """Return the URI path of the BIG-IP object.

        Not implemented because the current implementation only
        manages Monitor sub-classes.
        """
        raise NotImplementedError("No default monitor implemented")
