def test_get_health_check(client):
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json == {"success": True}
