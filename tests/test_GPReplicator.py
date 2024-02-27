# -*- coding: utf-8 -*-
# Author: Timur Gilmullin


import pytest
from pathlib import Path
from gpreplicator import GPReplicator


class TestGPReplicatorMethods:

    @pytest.fixture(scope="function", autouse=True)
    def init(self):
        GPReplicator.uLogger.level = 50  # Disable debug logging while test, logger CRITICAL = 50
        GPReplicator.uLogger.handlers[0].level = 50  # Disable debug logging for STDOUT
        GPReplicator.uLogger.handlers[1].level = 50  # Disable debug logging for log.txt

        # set up default parameters:
        self.project = GPReplicator.GPReplicator()
        self.token = 111

    def test__ParseJSONCheckType(self):
        assert isinstance(self.project._ParseJSON(rawData="{}"), dict), "Not dict type returned!"

    def test__ParseJSONPositive(self):
        testData = [
            ("{}", {}), ('{"x":123}', {"x": 123}), ('{"x":""}', {"x": ""}),
            ('{"abc": "123", "xyz": 123}', {"abc": "123", "xyz": 123}),
            ('{"abc": {"abc": "123", "xyz": 123}}', {"abc": {"abc": "123", "xyz": 123}}),
            ('{"abc": {"abc": "", "xyz": 0}}', {"abc": {"abc": "", "xyz": 0}}),
        ]

        for test in testData:
            result = self.project._ParseJSON(rawData=test[0])

            assert result == test[1], 'Expected: `_ParseJSON(rawData="{}", debug=False) == {}`, actual: `{}`'.format(test[0], test[1], result)

    def test__ParseJSONNegative(self):
        testData = [
            ("[]", []), ("{}", {}), ("{[]}", {}), ([], {}), (123, {}), ("123", 123), (None, {}), ("some string", {}),
        ]

        for test in testData:
            result = self.project._ParseJSON(rawData=test[0])

            assert result == test[1], "Unexpected output!"
