from rest_framework.test import APIClient

client = APIClient()


def test_brokers():
    response = client.get("/brokers/")
    assert response.status_code == 200, f"{response}"
