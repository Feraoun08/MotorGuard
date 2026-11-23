from backend.ingestion.event_key import generate_event_key


def test_same_payload_same_key():

    payload = {
        "motor_id": "MOTOR_01",
        "factory_id": "FACTORY_01",
        "value": 10,
    }

    first = generate_event_key(payload)
    second = generate_event_key(payload)

    assert first == second


def test_dictionary_order_does_not_change_key():

    first_payload = {
        "motor_id": "MOTOR_01",
        "factory_id": "FACTORY_01",
    }

    second_payload = {
        "factory_id": "FACTORY_01",
        "motor_id": "MOTOR_01",
    }

    assert (
        generate_event_key(first_payload)
        == generate_event_key(second_payload)
    )


def test_changed_payload_changes_key():

    first_payload = {
        "motor_id": "MOTOR_01",
        "temperature": 25.0,
    }

    second_payload = {
        "motor_id": "MOTOR_01",
        "temperature": 26.0,
    }

    assert (
        generate_event_key(first_payload)
        != generate_event_key(second_payload)
    )