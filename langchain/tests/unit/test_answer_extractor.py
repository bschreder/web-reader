import types

from src.agent import _extract_answer


class DummyMessage:
    def __init__(self, content):
        self.content = content


def test_extract_from_messages_list_of_dicts():
    res = {"messages": [{"content": "msg1"}, {"content": "msg2"}]}
    assert _extract_answer(res) == "msg1\nmsg2"


def test_extract_from_messages_list_of_objects():
    res = {"messages": [DummyMessage("a"), DummyMessage("b")]}
    assert _extract_answer(res) == "a\nb"


def test_extract_from_choices():
    res = {"choices": [{"content": "choice1"}]}
    assert "choice1" in _extract_answer(res)


def test_fallback_stringification():
    class X:
        def __str__(self):
            return "custom"

    assert _extract_answer(X()) == "custom"


def test_extract_from_output_key():
    res = {"output": "42"}
    assert _extract_answer(res) == "42"


def test_extract_from_text_key():
    res = {"text": "hello"}
    assert _extract_answer(res) == "hello"


def test_extract_from_messages_dicts():
    res = {"messages": [{"content": "part1"}, {"content": "part2"}]}
    assert _extract_answer(res) == "part1\npart2"


def test_extract_from_messages_objects():
    msg1 = types.SimpleNamespace(content="obj1")
    msg2 = types.SimpleNamespace(content="obj2")
    res = {"messages": [msg1, msg2]}
    assert _extract_answer(res) == "obj1\nobj2"


def test_fallback_to_str():
    class Weird:
        def __str__(self):
            return "weird"

    res = Weird()
    assert _extract_answer(res) == "weird"
