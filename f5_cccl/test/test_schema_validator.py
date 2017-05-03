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

import pytest
import json
import jsonschema
from jsonschema import validators
from jsonschema import Draft4Validator


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.iteritems():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
                validator, properties, instance, schema,):
            yield error

    return validators.extend(
        validator_class, {"properties": set_defaults}
    )


@pytest.fixture
def schema_validator():
    """Validator fixture."""
    DefaultValidatingDraft4Validator = extend_with_default(Draft4Validator)
    return DefaultValidatingDraft4Validator


@pytest.fixture
def schema():
    """Schema fixture."""
    json_schema = 'schemas/tests/cccl.json'

    # load schema
    with open(json_schema) as f:
        schema_data = f.read()
        schema = json.loads(schema_data)
        Draft4Validator.check_schema(schema)

    return schema


def validate(schema_validator, schema, services):
    """Validate a service description."""
    try:
        schema_validator(schema).validate(services)
        return 'Schema Valid'
    except jsonschema.exceptions.SchemaError:
        return 'Schema Error'
    except jsonschema.exceptions.ValidationError:
        return 'Validator Error'


def validate_required(validator, schema, services, rsc_type, rscs):
    """Validate required values."""
    required = schema['definitions'][rsc_type]['required']
    for req in required:
        for idx, rsc in enumerate(services[rscs]):
            tmp = rsc[req]
            del rsc[req]
            services[rscs][idx] = rsc

            result = validate(validator, schema, services)
            assert result == 'Validator Error'

            rsc[req] = tmp
            services[rscs][idx] = rsc


def validate_defaults(validator, schema, services, rsc_type, rscs):
    """Validate default values."""
    properties = schema['definitions'][rsc_type]['properties']

    for key, value in properties.iteritems():
        default = value.get('default')
        if default is not None:
            for idx, rsc in enumerate(services[rscs]):
                assert rsc[key] == default


def validate_string(validator, schema, services, rsc, key, prop):
    """Validate a string property."""
    tmp = rsc.get(key)
    if tmp is not None:
        # not a string
        rsc[key] = 100
        result = validate(validator, schema, services)
        assert result == 'Validator Error'
        rsc[key] = tmp

    minLength = prop.get('minLength')
    if minLength is not None and minLength > 0:
        tmp = rsc.get(key)
        if tmp is not None:
            # less than min length
            rsc[key] = ''
            result = validate(validator, schema, services)
            assert result == 'Validator Error'
            rsc[key] = tmp

    maxLength = prop.get('maxLength')
    if maxLength is not None:
        tmp = rsc.get(key)
        if tmp is not None:
            # greater than max length
            rsc[key] = 'x' * (maxLength + 1)
            result = validate(validator, schema, services)
            assert result == 'Validator Error'
            rsc[key] = tmp


def validate_integer(validator, schema, services, rsc, key, prop):
    """Validate an integer property."""
    tmp = rsc.get(key)
    if tmp is not None:
        # not an integer
        rsc[key] = 'This is not a number!'
        result = validate(validator, schema, services)
        assert result == 'Validator Error'
        rsc[key] = tmp

    minimum = prop.get('minimum')
    if minimum is not None:
        tmp = rsc.get(key)
        if tmp is not None:
            # less than min value
            rsc[key] = minimum - 1
            result = validate(validator, schema, services)
            assert result == 'Validator Error'
            rsc[key] = tmp

    maximum = prop.get('maximum')
    if maximum is not None:
        tmp = rsc.get(key)
        if tmp is not None:
            # greater than max value
            rsc[key] = maximum + 1
            result = validate(validator, schema, services)
            assert result == 'Validator Error'
            rsc[key] = tmp


def validate_types(validator, schema, services, rsc_type, rscs):
    """Validate the basic types in the schema."""
    properties = schema['definitions'][rsc_type]['properties']

    for key, value in properties.iteritems():
        val_type = value.get('type')
        if val_type is not None:
            for idx, rsc in enumerate(services[rscs]):
                # check strings
                if val_type == 'string':
                    validate_string(validator, schema, services, rsc, key,
                                    value)

                # check integers
                if val_type == 'integer':
                    validate_integer(validator, schema, services, rsc, key,
                                     value)

                # check enums
                enum = value.get('enum')
                if enum is not None:
                    tmp = rsc.get(key)
                    if tmp is not None:
                        rsc[key] = 'This string will match no enums'
                        result = validate(validator, schema, services)
                        assert result == 'Validator Error'
                        rsc[key] = tmp


def test_resources(schema_validator, schema):
    """Load a service description and validate ir with the schema."""
    svcfile = 'f5_cccl/test/service.json'
    services = json.loads(open(svcfile, 'r').read())

    result = validate(schema_validator, schema, services)
    assert result == 'Schema Valid'

    resources = {'virtualServerType': 'virtualServers',
                 'poolType': 'pools',
                 'l7PolicyType': 'l7Policies',
                 'healthMonitorType': 'monitors'}

    for key, value in resources.iteritems():
        validate_required(schema_validator, schema, services, key, value)
        validate_defaults(schema_validator, schema, services, key, value)
        validate_types(schema_validator, schema, services, key, value)
