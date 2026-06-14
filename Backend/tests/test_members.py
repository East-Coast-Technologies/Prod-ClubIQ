import uuid
import pytest
from app import db
from app.models import User, Club, ClubMember


def auth_header(token: str = "token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def set_token(monkeypatch, clerk_id: str):
    monkeypatch.setattr("app.auth.decorators.verify_clerk_token", lambda token: {"sub": clerk_id})


def create_user(app, clerk_id: str, name: str, email: str, username: str, role: str = "user"):
    with app.app_context():
        unique_suffix = uuid.uuid4().hex[:6]
        user = User(
            clerk_id=clerk_id,
            name=name,
            email=f"{unique_suffix}-{email}",
            username=f"{username}-{unique_suffix}",
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "clerk_id": user.clerk_id, "username": user.username}


def create_club(client, monkeypatch, creator, name: str):
    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post("/api/clubs/", json={"name": name}, headers=auth_header())
    assert resp.status_code == 201
    return resp.get_json()["id"]


def add_member(client, monkeypatch, acting_user, club_id: str, target_user_id: int, role: str = "member"):
    set_token(monkeypatch, acting_user["clerk_id"])
    return client.post(
        "/api/members/",
        json={"club_id": club_id, "user_id": target_user_id, "role": role},
        headers=auth_header(),
    )


@pytest.fixture(autouse=True)
def clean_members(app):
    with app.app_context():
        ClubMember.query.delete()
        Club.query.delete()
        User.query.filter(User.clerk_id != "clerk_admin").delete()
        db.session.commit()
    yield


def test_create_member_success(monkeypatch, client, app):
    creator = create_user(app, "clerk_creator", "Creator", "creator@example.com", "creator")
    target = create_user(app, "clerk_target", "Target", "target@example.com", "target")

    club_id = create_club(client, monkeypatch, creator, "Club A")

    resp = add_member(client, monkeypatch, creator, club_id, target["id"], role="member")

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["role"] == "member"

    with app.app_context():
        membership = ClubMember.query.filter_by(club_id=uuid.UUID(club_id), user_id=target["id"]).one()
        assert membership.role == "member"


def test_create_member_duplicate(monkeypatch, client, app):
    creator = create_user(app, "clerk_creator2", "Creator2", "creator2@example.com", "creator2")
    target = create_user(app, "clerk_target2", "Target2", "target2@example.com", "target2")
    club_id = create_club(client, monkeypatch, creator, "Club B")

    first = add_member(client, monkeypatch, creator, club_id, target["id"])
    assert first.status_code == 201

    dup = add_member(client, monkeypatch, creator, club_id, target["id"])
    assert dup.status_code == 400
    assert "already" in dup.get_json().get("error", "")


def test_update_member_role_by_admin(monkeypatch, client, app):
    creator = create_user(app, "clerk_creator3", "Creator3", "creator3@example.com", "creator3")
    target = create_user(app, "clerk_target3", "Target3", "target3@example.com", "target3")
    admin = {"id": 1, "clerk_id": "clerk_admin"}

    club_id = create_club(client, monkeypatch, creator, "Club C")
    resp = add_member(client, monkeypatch, creator, club_id, target["id"])
    membership_id = resp.get_json()["id"]

    set_token(monkeypatch, admin["clerk_id"])
    update_resp = client.put(
        f"/api/members/{membership_id}",
        json={"role": "moderator"},
        headers=auth_header(),
    )

    assert update_resp.status_code == 200
    assert update_resp.get_json()["role"] == "moderator"


def test_list_members_mine_filters(monkeypatch, client, app):
    user1 = create_user(app, "clerk_u1", "User1", "u1@example.com", "user1")
    user2 = create_user(app, "clerk_u2", "User2", "u2@example.com", "user2")

    club1 = create_club(client, monkeypatch, user1, "Club U1")
    add_member(client, monkeypatch, user1, club1, user1["id"])

    club2 = create_club(client, monkeypatch, user2, "Club U2")
    add_member(client, monkeypatch, user2, club2, user1["id"])

    set_token(monkeypatch, user1["clerk_id"])
    list_resp = client.get("/api/members/?mine=true", headers=auth_header())

    assert list_resp.status_code == 200
    payload = list_resp.get_json()
    assert len(payload) == 2
    club_ids = {item["club_id"] for item in payload}
    assert club_ids == {club1, club2}


def test_delete_member_by_creator(monkeypatch, client, app):
    creator = create_user(app, "clerk_del", "Del", "del@example.com", "deluser")
    target = create_user(app, "clerk_del_t", "DelT", "delt@example.com", "deltuser")

    club_id = create_club(client, monkeypatch, creator, "Club D")
    resp = add_member(client, monkeypatch, creator, club_id, target["id"])
    membership_id = resp.get_json()["id"]

    set_token(monkeypatch, creator["clerk_id"])
    delete_resp = client.delete(f"/api/members/{membership_id}", headers=auth_header())
    assert delete_resp.status_code == 200

    with app.app_context():
        assert db.session.get(ClubMember, uuid.UUID(membership_id)) is None


def test_v1_create_member_uses_configured_single_club(monkeypatch, client, app):
    creator = create_user(app, "clerk_v1_member_creator", "V1 Creator", "v1creator@example.com", "v1creator")
    target = create_user(app, "clerk_v1_member_target", "V1 Target", "v1target@example.com", "v1target")

    active_club_name = "clubIQ Members"
    club_id = create_club(client, monkeypatch, creator, active_club_name)

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post(
        "/api/v1/members/",
        json={"user_id": target["id"], "role": "member"},
        headers=auth_header(),
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["role"] == "member"
    assert body["club_id"] == club_id

    with app.app_context():
        membership = ClubMember.query.filter_by(
            club_id=uuid.UUID(club_id),
            user_id=target["id"],
        ).one()
        assert membership.role == "member"


def test_v1_create_member_rejects_client_club_id(monkeypatch, client, app):
    creator = create_user(app, "clerk_v1_member_reject", "V1 Reject", "v1reject@example.com", "v1reject")
    target = create_user(app, "clerk_v1_member_reject_target", "V1 Reject Target", "v1rejecttarget@example.com", "v1rejecttarget")

    active_club_name = "clubIQ Members Reject"
    create_club(client, monkeypatch, creator, active_club_name)
    other_club_id = create_club(client, monkeypatch, creator, "Other Members Club")

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, creator["clerk_id"])
    resp = client.post(
        "/api/v1/members/",
        json={"club_id": other_club_id, "user_id": target["id"], "role": "member"},
        headers=auth_header(),
    )

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "club_id is not accepted in v1"

    with app.app_context():
        assert ClubMember.query.filter_by(user_id=target["id"]).first() is None


def test_v1_list_members_uses_configured_single_club(monkeypatch, client, app):
    creator = create_user(app, "clerk_v1_member_list", "V1 List", "v1list@example.com", "v1list")
    target = create_user(app, "clerk_v1_member_list_target", "V1 List Target", "v1listtarget@example.com", "v1listtarget")

    active_club_name = "clubIQ Members List"
    active_club_id = create_club(client, monkeypatch, creator, active_club_name)
    other_club_id = create_club(client, monkeypatch, creator, "Other Members List")

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, creator["clerk_id"])
    client.post(
        "/api/v1/members/",
        json={"user_id": target["id"], "role": "member"},
        headers=auth_header(),
    )

    # Legacy route creates a member in another club to prove v1 list is scoped.
    add_member(client, monkeypatch, creator, other_club_id, creator["id"], role="member")

    set_token(monkeypatch, creator["clerk_id"])
    list_resp = client.get("/api/v1/members/", headers=auth_header())

    assert list_resp.status_code == 200
    payload = list_resp.get_json()
    club_ids = {item["club_id"] for item in payload}
    assert club_ids == {active_club_id}


def test_v1_list_members_rejects_client_club_id_query(monkeypatch, client, app):
    creator = create_user(app, "clerk_v1_member_query", "V1 Query", "v1query@example.com", "v1query")

    active_club_name = "clubIQ Members Query"
    create_club(client, monkeypatch, creator, active_club_name)

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, creator["clerk_id"])
    resp = client.get(
        "/api/v1/members/?club_id=bad-client-club",
        headers=auth_header(),
    )

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "club_id query param is not accepted in v1"


def test_v1_list_members_blocks_synced_non_member(monkeypatch, client, app):
    creator = create_user(app, "clerk_v1_members_owner", "V1 Owner", "v1owner@example.com", "v1owner")
    outsider = create_user(app, "clerk_v1_members_outsider", "V1 Outsider", "v1outsider@example.com", "v1outsider")

    active_club_name = "clubIQ Member Access"
    create_club(client, monkeypatch, creator, active_club_name)

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    set_token(monkeypatch, outsider["clerk_id"])
    response = client.get("/api/v1/members/", headers=auth_header())

    assert response.status_code == 403
    assert response.get_json()["message"] == "User is not a member of the configured club"


def test_v1_get_member_blocks_member_from_other_club(monkeypatch, client, app):
    creator = create_user(app, "clerk_v1_member_scope_owner", "V1 Scope Owner", "v1scopeowner@example.com", "v1scopeowner")
    target = create_user(app, "clerk_v1_member_scope_target", "V1 Scope Target", "v1scopetarget@example.com", "v1scopetarget")

    active_club_name = "clubIQ Member Scope"
    create_club(client, monkeypatch, creator, active_club_name)
    other_club_id = create_club(client, monkeypatch, creator, "Other Member Scope")

    app.config["SINGLE_CLUB_NAME"] = active_club_name

    other_resp = add_member(client, monkeypatch, creator, other_club_id, target["id"], role="member")
    assert other_resp.status_code == 201
    other_membership_id = other_resp.get_json()["id"]

    set_token(monkeypatch, creator["clerk_id"])
    response = client.get(f"/api/v1/members/{other_membership_id}", headers=auth_header())

    assert response.status_code == 404
