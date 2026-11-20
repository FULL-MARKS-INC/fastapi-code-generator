import copy
import pickle

import pytest

from fastapi_code_generator.parser import Operation, PythonEscapedString


def _operation() -> Operation:
    return Operation(
        method='get',
        path="/items/'+x+'/detail",
        summary='bad""" + x + """done',
        additional_responses={"404' + x + 'x": {'model': 'Error'}},
        tags=["it's"],
    )


# Not in 0.8.1: Operation must stay copyable after its values are escaped.
@pytest.mark.parametrize(
    'copier',
    [copy.copy, copy.deepcopy, lambda v: pickle.loads(pickle.dumps(v))],
    ids=['copy', 'deepcopy', 'pickle'],
)
def test_python_escaped_string_keeps_raw_and_escaped_value_when_copied(copier):
    value = PythonEscapedString.single_quoted("a'b")

    copied = copier(value)

    assert isinstance(copied, PythonEscapedString)
    assert str.__str__(copied) == r"a\'b"
    assert copied.raw == "a'b"


def test_operation_can_be_deep_copied():
    operation = _operation()

    copied = copy.deepcopy(operation)

    assert str.__str__(copied.path) == r"/items/\'+x+\'/detail"
    assert copied.path.raw == "/items/'+x+'/detail"
    assert str.__str__(copied.summary) == r'bad\"\"\" + x + \"\"\"done'
    assert [str.__str__(k) for k in copied.additional_responses] == [r"404\' + x + \'x"]
    assert [str.__str__(t) for t in copied.tags] == [r"it\'s"]
    assert copied.function_name == operation.function_name
