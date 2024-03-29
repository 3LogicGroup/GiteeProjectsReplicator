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
        self.projectModel.timeout = 60
        self.projectModel.retry = 10
        self.projectModel.gToken = None  # about ~60 requests are available without authentication
        self.projectModel.gOwner = "tim55667757"
        self.projectModel.gProject = "PriceGenerator"
        self.projectModel.gSHA = "master"

    def test__ParseJSONCheckType(self):
        assert isinstance(self.projectModel._ParseJSON(rawData="{}"), dict), "Not dict type returned"

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

            assert result == test[1], "Unexpected output"

    def test_SendAPIRequestCheckType(self):
        result = self.projectModel.SendAPIRequest(
            url=self.projectModel.gAPIGateway + f"/repos/{self.projectModel.gOwner}/{self.projectModel.gProject}/branches",
            reqType="GET",
        )

        assert isinstance(result, list) or isinstance(result, dict), "Not list, dictionary or list of dictionaries type returned"

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

        assert isinstance(result, dict), "Not dict type returned"

    def test_FilesPositive(self):
        self.projectModel.gRecursive = 1

        result = self.projectModel.Files()

        assert "tree" in result.keys(), f'"tree" not in result.keys()!'
        assert len(result['tree']) == 46, f'Expected: `46`, actual: `{len(result["tree"])}`'

        self.projectModel.gRecursive = 0

        result = self.projectModel.Files()

        assert "tree" in result.keys(), f'"tree" not in result.keys()'
        assert len(result['tree']) == 15, f'Expected: `15`, actual: `{len(result["tree"])}`'

    def test_FilesNegative(self):
        gSHA = self.projectModel.gSHA
        self.projectModel.gSHA = ""

        try:
            self.projectModel.Files()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gSHA = "0"

        result = self.projectModel.Files()

        assert "tree" in result.keys(), f'"tree" in result.keys()'
        assert len(result) == 4, f'Expected: `4`, actual: `{len(result)}`'
        assert len(result['tree']) == 0, f'Expected: `0`, actual: `{len(result["tree"])}`'

        self.projectModel.gSHA = gSHA

    def test_GetFileCheckType(self):
        result = self.projectModel.GetFile()

        assert isinstance(result, str), "Not str type returned"

    def test_GetFilePositive(self):
        gSHA = self.projectModel.gSHA
        self.projectModel.gSHA = "057e6382ef1052ac56e5e9184fdd4ef66bef2593"

        result = self.projectModel.GetFile()

        assert len(result) == 761, f'Expected: `761`, actual: `{len(result)}`'

        self.projectModel.gSHA = gSHA

    def test_GetFileNegative(self):
        gSHA = self.projectModel.gSHA
        self.projectModel.gSHA = "0"

        result = self.projectModel.GetFile()

        assert result == "", f'Expected: empty string, actual: `{result}`'

        self.projectModel.gSHA = gSHA

    def test_IssuesCheckType(self):
        result = self.projectModel.Issues()

        assert isinstance(result, list), "Not list of dictionaries type returned"

    def test_IssuesPositive(self):
        result = self.projectModel.Issues()

        assert len(result) > 0, f'Expected: `> 0`, actual: `{len(result)}`'

    def test_IssuesNegative(self):
        gOwner = self.projectModel.gOwner
        self.projectModel.gOwner = ""

        try:
            self.projectModel.Issues()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gOwner = gOwner

        gProject = self.projectModel.gProject
        self.projectModel.gProject = ""

        try:
            self.projectModel.Issues()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gProject = gProject

    def test_MilestonesCheckType(self):
        result = self.projectModel.Milestones()

        assert isinstance(result, list), "Not list of dictionaries type returned"

    def test_MilestonesPositive(self):
        result = self.projectModel.Milestones()

        assert len(result) == 0, f'Expected: `0`, actual: `{len(result)}`'

    def test_MilestonesNegative(self):
        gOwner = self.projectModel.gOwner
        self.projectModel.gOwner = ""

        try:
            self.projectModel.Milestones()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gOwner = gOwner

        gProject = self.projectModel.gProject
        self.projectModel.gProject = ""

        try:
            self.projectModel.Milestones()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gProject = gProject

    def test_ReleasesCheckType(self):
        result = self.projectModel.Releases()

        assert isinstance(result, list), "Not list of dictionaries type returned"

    def test_ReleasesPositive(self):
        result = self.projectModel.Releases()

        assert len(result) == 0, f'Expected: `0`, actual: `{len(result)}`'

    def test_ReleasesNegative(self):
        gOwner = self.projectModel.gOwner
        self.projectModel.gOwner = ""

        try:
            self.projectModel.Releases()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gOwner = gOwner

        gProject = self.projectModel.gProject
        self.projectModel.gProject = ""

        try:
            self.projectModel.Releases()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gProject = gProject

    def test_TagsCheckType(self):
        result = self.projectModel.Tags()

        assert isinstance(result, list), "Not list of dictionaries type returned"

    def test_TagsPositive(self):
        result = self.projectModel.Tags()

        assert len(result) == 7, f'Expected: `7`, actual: `{len(result)}`'

    def test_TagsNegative(self):
        gOwner = self.projectModel.gOwner
        self.projectModel.gOwner = ""

        try:
            self.projectModel.Tags()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gOwner = gOwner

        gProject = self.projectModel.gProject
        self.projectModel.gProject = ""

        try:
            self.projectModel.Tags()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gProject = gProject

    def test_BranchesCheckType(self):
        result = self.projectModel.Branches()

        assert isinstance(result, list), "Not list of dictionaries type returned"

    def test_BranchesPositive(self):
        result = self.projectModel.Branches()

        assert len(result) == 2, f'Expected: `2`, actual: `{len(result)}`'

    def test_BranchesNegative(self):
        gOwner = self.projectModel.gOwner
        self.projectModel.gOwner = ""

        try:
            self.projectModel.Branches()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gOwner = gOwner

        gProject = self.projectModel.gProject
        self.projectModel.gProject = ""

        try:
            self.projectModel.Branches()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gProject = gProject

    def test_RepositoriesCheckType(self):
        gToken = self.projectModel.gToken
        self.projectModel.gToken = "123"

        result = self.projectModel.Repositories()

        assert isinstance(result, list), "Not list of dictionaries type returned"

        self.projectModel.gToken = gToken

    def test_RepositoriesPositive(self):
        gToken = self.projectModel.gToken
        self.projectModel.gToken = "123"

        result = self.projectModel.Repositories()

        assert len(result) == 0, f'Expected: `0`, actual: `{len(result)}`'

        self.projectModel.gToken = gToken

    def test_RepositoriesNegative(self):
        gToken = self.projectModel.gToken
        self.projectModel.gToken = None

        try:
            self.projectModel.Repositories()

            assert False, 'Expected exception `Some parameters are required`'

        except Exception:
            assert True

        self.projectModel.gToken = gToken
