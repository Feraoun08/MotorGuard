from backend.ingestion.inbox_worker import InboxWorker


class DummyRepository:
    pass


class DummyInflux:
    pass


def create_worker(
    base=2,
    maximum=300,
):
    return InboxWorker(
        repository=DummyRepository(),
        influx_store=DummyInflux(),
        retry_base_seconds=base,
        retry_max_seconds=maximum,
    )


def test_retry_delay_increases():

    worker = create_worker()

    first = worker._calculate_retry_delay(0)
    second = worker._calculate_retry_delay(1)
    third = worker._calculate_retry_delay(2)

    # Jitter may be added, but the retry interval
    # should increase across early retry attempts.
    assert first >= 2
    assert second >= 4
    assert third >= 8


def test_retry_delay_is_capped():

    worker = create_worker(
        base=2,
        maximum=20,
    )

    delay = worker._calculate_retry_delay(20)

    assert delay <= 24