from pytest_unordered import unordered
from fhirflat.util import group_keys


def test_group_keys():
    data = [
        "code.code",
        "code.text",
        "status",
        "class.code",
        "class.text",
        "priority.code",
        "priority.text",
        "type.code",
        "type.text",
        "participant.type.code",
        "participant.actor.reference",
    ]
    result = group_keys(data)

    assert result == {
        "code": unordered(["code.code", "code.text"]),
        "class": unordered(["class.code", "class.text"]),
        "priority": unordered(["priority.code", "priority.text"]),
        "type": unordered(["type.code", "type.text"]),
        "participant": unordered(
            ["participant.type.code", "participant.actor.reference"]
        ),
    }
