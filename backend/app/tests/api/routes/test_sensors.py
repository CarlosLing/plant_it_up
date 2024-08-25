from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.sensor import create_random_sensor


def test_create_sensor(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "test sensor",
            "measurement": "test measurement",
            "location": "test location",
            "description": "test description"}
    response = client.post(
        f"{settings.API_V1_STR}/sensors/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["measurement"] == data["measurement"]
    assert content["location"] == data["location"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_sensor(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    sensor = create_random_sensor(db)
    response = client.get(
        f"{settings.API_V1_STR}/sensors/{sensor.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == sensor.name
    assert content["measurement"] == sensor.measurement
    assert content["location"] == sensor.location
    assert content["description"] == sensor.description
    assert content["id"] == sensor.id
    assert content["owner_id"] == sensor.owner_id


def test_read_sensor_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/sensors/99999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Sensor not found"


def test_read_sensor_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    sensor = create_random_sensor(db)
    response = client.get(
        f"{settings.API_V1_STR}/sensors/{sensor.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_items(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_sensor(db)
    create_random_sensor(db)
    response = client.get(
        f"{settings.API_V1_STR}/sensors/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_sensor(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    sensor = create_random_sensor(db)
    data = {"name": "Updated name", "measurement": "Updated measurement", "location": "Updated location", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/sensors/{sensor.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["measurement"] == data["measurement"]
    assert content["location"] == data["location"]
    assert content["description"] == data["description"]
    assert content["id"] == sensor.id
    assert content["owner_id"] == sensor.owner_id


def test_update_sensor_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated name", "measurement": "Updated measurement", "location": "Updated location", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/sensors/99999",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Sensor not found"


def test_update_sensor_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    sensor = create_random_sensor(db)
    data = {"name": "Updated name", "measurement": "Updated measurement", "location": "Updated location", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/sensors/{sensor.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_sensor(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    sensor = create_random_sensor(db)
    response = client.delete(
        f"{settings.API_V1_STR}/sensors/{sensor.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Sensor deleted successfully"


def test_delete_sensor_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/sensors/999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Sensor not found"


def test_delete_sensor_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    sensor = create_random_sensor(db)
    response = client.delete(
        f"{settings.API_V1_STR}/sensors/{sensor.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
