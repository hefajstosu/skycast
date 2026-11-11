def test_add_and_list_favorite(client, mock_api):
    response = client.post("/api/favorites", json={"city": "krakow", "note": "university"})

    assert response.status_code == 201
    assert response.json()["city"] == "Kraków"  # name normalized by geocoding
    assert [f["city"] for f in client.get("/api/favorites").json()] == ["Kraków"]


def test_duplicate_favorite_returns_409(client, mock_api):
    client.post("/api/favorites", json={"city": "Kraków"})
    assert client.post("/api/favorites", json={"city": "krakow"}).status_code == 409


def test_unknown_city_cannot_be_favorite(client, mock_api):
    assert client.post("/api/favorites", json={"city": "Atlantis"}).status_code == 404
    assert client.get("/api/favorites").json() == []


def test_delete_favorite(client, mock_api):
    favorite_id = client.post("/api/favorites", json={"city": "Kraków"}).json()["id"]

    assert client.delete(f"/api/favorites/{favorite_id}").status_code == 204
    assert client.delete(f"/api/favorites/{favorite_id}").status_code == 404
    assert client.get("/api/favorites").json() == []


def test_favorites_weather(client, mock_api):
    client.post("/api/favorites", json={"city": "Kraków"})

    data = client.get("/api/favorites/weather").json()
    assert len(data) == 1
    assert data[0]["favorite"]["city"] == "Kraków"
    assert data[0]["current"]["temperature"] == 6.4


def test_index_page_renders(client, mock_api):
    client.post("/api/favorites", json={"city": "Kraków"})

    response = client.get("/", params={"city": "Kraków"})
    assert response.status_code == 200
    assert "6°C" in response.text
    assert "In favorites" in response.text


def test_index_page_unknown_city(client, mock_api):
    response = client.get("/", params={"city": "Atlantis"})
    assert response.status_code == 404
    assert "City not found" in response.text
