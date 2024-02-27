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
        self.projectModel = GPReplicator.GPReplicator()
        self.projectModel.gAPIGateway = "https://gitee.com/api/v5"
        self.projectModel.timeout = 180
        self.projectModel.gToken = 111
        self.projectModel.gOwner = "tim55667757"
        self.projectModel.gProject = "PriceGenerator"
        self.projectModel.gSHA = "master"

    def test__ParseJSONCheckType(self):
        assert isinstance(self.projectModel._ParseJSON(rawData="{}"), dict), "Not dict type returned!"

    def test__ParseJSONPositive(self):
        testData = [
            ("{}", {}), ('{"x":123}', {"x": 123}), ('{"x":""}', {"x": ""}),
            ('{"abc": "123", "xyz": 123}', {"abc": "123", "xyz": 123}),
            ('{"abc": {"abc": "123", "xyz": 123}}', {"abc": {"abc": "123", "xyz": 123}}),
            ('{"abc": {"abc": "", "xyz": 0}}', {"abc": {"abc": "", "xyz": 0}}),
        ]

        for test in testData:
            result = self.projectModel._ParseJSON(rawData=test[0])

            assert result == test[1], f'Expected: `_ParseJSON(rawData="{test[0]}", debug=False) == {test[1]}`, actual: `{result}`'

    def test__ParseJSONNegative(self):
        testData = [
            ("[]", []), ("{}", {}), ("{[]}", {}), ([], {}), (123, {}), ("123", 123), (None, {}), ("some string", {}),
        ]

        for test in testData:
            result = self.projectModel._ParseJSON(rawData=test[0])

            assert result == test[1], "Unexpected output!"

    def test_SendAPIRequestCheckType(self):
        result = self.projectModel.SendAPIRequest(
            url=self.projectModel.gAPIGateway + f"/repos/{self.projectModel.gOwner}/{self.projectModel.gProject}/branches",
            reqType="GET",
        )

        assert isinstance(result, list), "Not list of dictionaries type returned!"

    def test_SendAPIRequestPositive(self):
        testData = (self.projectModel.gAPIGateway + f"/repos/{self.projectModel.gOwner}/{self.projectModel.gProject}/branches", ["develop", "master"])

        result = self.projectModel.SendAPIRequest(url=testData[0], reqType="GET")

        assert len(result) == len(testData[1]), f'Expected: `{len(testData[1])}`, actual: `{len(result)}`'
        assert result[0]["name"] == testData[1][0], 'Expected: `{testData[1][0]}`, actual: `{result[0]["name"]}`'
        assert result[1]["name"] == testData[1][1], 'Expected: `{testData[1][1]}`, actual: `{result[1]["name"]}`'

    def test_SendAPIRequestNegative(self):
        testData = (self.projectModel.gAPIGateway + f"/repos/{self.projectModel.gOwner}/{self.projectModel.gProject}/milestones", [])

        result = self.projectModel.SendAPIRequest(url=testData[0], reqType="GET")

        assert len(result) == len(testData[1]), f'Expected: `{len(testData[1])}`, actual: `{len(result)}`'
        assert result == testData[1], 'Expected: `{testData[1]}`, actual: `{result}`'

    def test_FilesCheckType(self):
        result = self.projectModel.Files()

        assert isinstance(result, dict), "Not dict type returned!"

    def test_FilesPositive(self):
        self.projectModel.gRecursive = 1

        result = self.projectModel.Files()

        assert "tree" in result.keys(), f'"tree" not in result.keys()!'
        assert len(result['tree']) == 46, f'Expected: `46`, actual: `{len(result["tree"])}`'

        self.projectModel.gRecursive = 0

        result = self.projectModel.Files()

        assert "tree" in result.keys(), f'"tree" not in result.keys()!'
        assert len(result['tree']) == 15, f'Expected: `15`, actual: `{len(result["tree"])}`'

    def test_FilesNegative(self):
        temp = self.projectModel.gSHA
        self.projectModel.gSHA = ""

        try:
            self.projectModel.Files()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gSHA = "0"

        result = self.projectModel.Files()

        assert "tree" in result.keys(), f'"tree" in result.keys()!'
        assert len(result) == 4, f'Expected: `4`, actual: `{len(result)}`'
        assert len(result['tree']) == 0, f'Expected: `0`, actual: `{len(result["tree"])}`'

        self.projectModel.gSHA = temp
