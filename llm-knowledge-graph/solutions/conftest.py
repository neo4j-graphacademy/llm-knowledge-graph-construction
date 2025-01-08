import builtins
import importlib
import io
import sys

import pytest
from pytest import MonkeyPatch

from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def load_env_vars():
    load_dotenv()

class TestHelpers:
    @staticmethod
    def run_module(monkeypatch: MonkeyPatch, module_name: str, input_values: list[str] = [] ) -> str:
        """
        Runs a module (.py file) to completion.
        stdin input_values can be provided as a list of strings.
        stdout output is returned as a string.
        """

        def mocked_input(prompt: str = "", return_values: list[str] = input_values):
            if len(return_values) == 0:
                raise Exception("Test error - Ran out of input values")
            return return_values.pop(0)

        mocked_stdout = io.StringIO()

        with monkeypatch.context() as m:
            m.setattr(builtins, "input", mocked_input)
            m.setattr(sys, "stdout", mocked_stdout)

            sys.modules.pop(module_name, None)
            importlib.import_module(name=module_name, package="files")

        return mocked_stdout.getvalue().strip()
    
    @staticmethod
    def run_cypher_file(graph, file_path):
        with open(file_path, "r") as file:
            cyphers = file.read()
            result = []
            for cypher in cyphers.split(";"):
                if cypher.strip() != "":
                    result.append(TestHelpers.run_cypher(graph, cypher))
            return result
        
    @staticmethod
    def run_cypher(graph, cypher):
        return graph.query(cypher)
    
@pytest.fixture()
def test_helpers():
    return TestHelpers
