import uuid
from app import db
from app.models import User, Activity


def auth_header(token: str = "token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def set_token(monkeypatch, clerk_id: str):
    monkeypatch.setattr("app.auth.decorators.verify_clerk_token", lambda token: {"sub": clerk_id})


def create_user(app, clerk_id: str, name: str, email: str, username: str, role: str = "user"):
    with app.app_context():
        user = User(clerk_id=clerk_id, name=name, email=email, username=username, role=role)
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "clerk_id": user.clerk_id, "username": user.username}


def create_club(client, monkeypatch, creator, name: str):
    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post("/api/clubs/", json={"name": name}, headers=auth_header())
    assert resp.status_code == 201
    return resp.get_json()["id"]


def test_create_activity_success(monkeypatch, client, app):
    creator = create_user(app, "clerk_act_creator", "Creator", "creator@ex.com", "creator", role="admin")
    club_id = create_club(client, monkeypatch, creator, "Activity Club")

    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post(
        "/api/activities/create/",
        json={"title": "Movie Night", "description": "Watch films", "club_id": club_id},
        headers=auth_header(),
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["Details"]["title"] == "Movie Night"

    with app.app_context():
        act = Activity.query.filter_by(title="Movie Night").one()
        assert act.club_id == uuid.UUID(club_id)
        assert act.author_id == creator["id"]


def test_create_activity_invalid_club(monkeypatch, client, app):
    creator = create_user(app, "clerk_any", "Any", "any@ex.com", "any", role="admin")
    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post(
        "/api/activities/create/",
        json={"title": "Invalid Club", "club_id": "not-a-uuid"},
        headers=auth_header(),
    )
    assert resp.status_code == 400


def test_create_activity_duplicate(monkeypatch, client, app):
    creator = create_user(app, "clerk_act_dup", "Creator", "creator2@ex.com", "creator2", role="admin")
    club_id = create_club(client, monkeypatch, creator, "Dup Club")

    set_token(monkeypatch, creator["clerk_id"])
    first = client.post(
        "/api/activities/create/",
        json={"title": "Weekly", "club_id": club_id},
        headers=auth_header(),
    )
    assert first.status_code == 201

    dup = client.post(
        "/api/activities/create/",
        json={"title": "Weekly", "club_id": club_id},
        headers=auth_header(),
    )
    assert dup.status_code == 400


def test_list_activities(monkeypatch, client, app):
    creator = create_user(app, "clerk_act_list", "Creator", "creator3@ex.com", "creator3", role="admin")
    club_id = create_club(client, monkeypatch, creator, "List Club")

    set_token(monkeypatch, creator["clerk_id"])
    client.post(
        "/api/activities/create/",
        json={"title": "Event1", "club_id": club_id},
        headers=auth_header(),
    )
    client.post(
        "/api/activities/create/",
        json={"title": "Event2", "club_id": club_id},
        headers=auth_header(),
    )

    set_token(monkeypatch, creator["clerk_id"])
    list_resp = client.get(f"/api/activities/{club_id}/", headers=auth_header())
    assert list_resp.status_code == 200
    titles = [item["title"] for item in list_resp.get_json()]
    assert titles == ["Event2", "Event1"]


def test_v1_create_activity_uses_configured_single_club(monkeypatch, client, app):
    creator = create_user(
        app,
        "clerk_v1_act_creator",
        "V1 Creator",
        "v1creator@ex.com",
        "v1creator",
        role="admin",
    )
    active_club_name = "clubIQ Activity"
    club_id = create_club(client, monkeypatch, creator, active_club_name)

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post(
        "/api/v1/activities/",
        json={"title": "V1 Movie Night", "description": "Single club event"},
        headers=auth_header(),
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["Details"]["title"] == "V1 Movie Night"

    with app.app_context():
        activity = Activity.query.filter_by(title="V1 Movie Night").one()
        assert activity.club_id == uuid.UUID(club_id)
        assert activity.author_id == creator["id"]


def test_v1_create_activity_rejects_client_club_id(monkeypatch, client, app):
    creator = create_user(
        app,
        "clerk_v1_act_reject",
        "V1 Reject",
        "v1reject@ex.com",
        "v1reject",
        role="admin",
    )
    active_club_name = "clubIQ Reject"
    #configured_club_id = create_club(client, monkeypatch, creator, active_club_name)
    create_club(client, monkeypatch, creator, active_club_name)
    other_club_id = create_club(client, monkeypatch, creator, "Other Club Reject")

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post(
        "/api/v1/activities/",
        json={"title": "Bad V1 Event", "club_id": other_club_id},
        headers=auth_header(),
    )

    assert resp.status_code == 400
    assert resp.get_json()["message"] == "club_id is not accepted in v1"

    with app.app_context():
        assert Activity.query.filter_by(title="Bad V1 Event").first() is None


def test_v1_list_activities_uses_configured_single_club(monkeypatch, client, app):
    creator = create_user(
        app,
        "clerk_v1_act_list",
        "V1 List",
        "v1list@ex.com",
        "v1list",
        role="admin",
    )
    active_club_name = "clubIQ List"
    create_club(client, monkeypatch, creator, active_club_name)

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, creator["clerk_id"])
    client.post(
        "/api/v1/activities/",
        json={"title": "V1 Event 1"},
        headers=auth_header(),
    )
    client.post(
        "/api/v1/activities/",
        json={"title": "V1 Event 2"},
        headers=auth_header(),
    )

    set_token(monkeypatch, creator["clerk_id"])
    list_resp = client.get("/api/v1/activities/", headers=auth_header())

    assert list_resp.status_code == 200
    titles = [item["title"] for item in list_resp.get_json()]
    assert titles == ["V1 Event 2", "V1 Event 1"]


def test_v1_list_activities_blocks_synced_non_member(monkeypatch, client, app):
    creator = create_user(
        app,
        "clerk_v1_act_owner",
        "V1 Owner",
        "v1owner@ex.com",
        "v1owner",
        role="admin",
    )
    outsider = create_user(
        app,
        "clerk_v1_act_outsider",
        "V1 Outsider",
        "v1outsider@ex.com",
        "v1outsider",
        role="user",
    )

    active_club_name = "clubIQ Activity Access"
    create_club(client, monkeypatch, creator, active_club_name)

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, outsider["clerk_id"])
    response = client.get("/api/v1/activities/", headers=auth_header())

    assert response.status_code == 403
    assert response.get_json()["message"] == "User is not a member of the configured club"
