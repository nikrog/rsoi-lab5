from mocks.gateway_mock import get_hotels, get_loyalty, get_reservation


def test_get_hotels():
    assert get_hotels().status == '200 OK'


def test_get_loyalty_pos():
    assert get_loyalty("Test Max").status == '200 OK'


def test_get_loyalty_neg():
    assert get_loyalty("New user").status == '400 BAD REQUEST'


def test_get_reservation_pos():
    response = get_reservation("155161bb-badd-4fa8-9d90-87c9a82b0668",
                           "Test Max")
    assert response.status == '200 OK'


def test_get_reservation_neg():
    assert get_reservation("155161bb-badd-4fa8-9d90-87c9a82b0668",
                           "New user").status == '400 BAD REQUEST'
