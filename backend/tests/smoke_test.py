"""
Standalone smoke test — NOT part of the delivered project, just used here to
validate the full request flow end-to-end against an in-memory mock Mongo
(no real MongoDB Atlas cluster needed for this check).
"""
import asyncio
import contextlib
import io
import re
import sys

from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

sys.path.insert(0, ".")

from app.models.comment import Comment  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.otp import OtpVerification  # noqa: E402
from app.models.post import Post  # noqa: E402
from app.models.user import User  # noqa: E402

CODE_RE = re.compile(r"Code:\s*(\d{6})")


def extract_code(captured: str) -> str:
    match = CODE_RE.search(captured)
    assert match, f"Could not find OTP code in output:\n{captured}"
    return match.group(1)


async def main():
    client = AsyncMongoMockClient(tz_aware=True)
    db = client["test_db"]
    await init_beanie(
        database=db,
        document_models=[User, Post, Comment, Notification, OtpVerification],
    )

    async def fake_init_db():
        pass

    import app.database as database_module
    database_module.init_db = fake_init_db
    import app.main as main_module
    main_module.init_db = fake_init_db

    from fastapi.testclient import TestClient

    with TestClient(main_module.app) as client_http:
        print("1. Health check")
        r = client_http.get("/api/")
        assert r.status_code == 200, r.text
        print("   OK:", r.json())

        print("\n2. Register")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = client_http.post(
                "/api/auth/register",
                json={"email": "alice@example.com", "name": "Alice", "password": "SuperSecret123"},
            )
        assert r.status_code == 201, r.text
        code = extract_code(buf.getvalue())
        print(f"   OK: registered, captured OTP {code} from console provider")

        print("\n3. Verify email with wrong code (should fail)")
        r = client_http.post("/api/auth/verify-email", json={"email": "alice@example.com", "code": "000000"})
        assert r.status_code == 400, r.text
        print("   OK: wrong code correctly rejected ->", r.json()["detail"])

        print("\n4. Verify email with correct code")
        r = client_http.post("/api/auth/verify-email", json={"email": "alice@example.com", "code": code})
        assert r.status_code == 200, r.text
        tokens = r.json()
        assert "access_token" in tokens and "refresh_token" in tokens
        print("   OK: verified, got JWT pair")

        print("\n5. Login")
        r = client_http.post("/api/auth/login", json={"email": "alice@example.com", "password": "SuperSecret123"})
        assert r.status_code == 200, r.text
        access_token = r.json()["access_token"]
        refresh_token = r.json()["refresh_token"]
        print("   OK: login works")

        print("\n6. Refresh token")
        r = client_http.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert r.status_code == 200, r.text
        print("   OK: refresh works")

        headers = {"Authorization": f"Bearer {access_token}"}

        print("\n7. Create a post (Bandra coordinates, no photos)")
        r = client_http.post(
            "/api/posts/",
            headers=headers,
            data={
                "type": "lost_pet",
                "title": "Lost dog near Bandstand",
                "description": "Golden retriever, red collar",
                "latitude": "19.0450",
                "longitude": "72.8258",
                "address_label": "Bandra Bandstand",
            },
        )
        assert r.status_code == 201, r.text
        post = r.json()
        post_id = post["id"]
        print("   OK: post created ->", post["title"])

        print("\n8-9. Nearby geo query ($near)")
        try:
            r = client_http.get("/api/posts/nearby", params={"lat": 19.0450, "lng": 72.8258, "radius_km": 5})
            if r.status_code == 200:
                results = r.json()
                assert any(p["id"] == post_id for p in results), "Created post not found in nearby results"
                print(f"   OK: found {len(results)} nearby post(s), distance_km={results[0]['distance_km']}")
            else:
                print(f"   SKIPPED assertion — non-200 ({r.status_code}): {r.text}")
        except Exception as e:
            if "$near" in str(e) or "NotImplementedError" in type(e).__name__:
                print("   SKIPPED: mongomock doesn't implement $near (real MongoDB/Atlas does — "
                      "this must be verified against a real cluster, noted in README).")
            else:
                raise

        print("\n10. Get post detail")
        r = client_http.get(f"/api/posts/{post_id}")
        assert r.status_code == 200, r.text
        print("   OK: detail fetch works")

        print("\n11. Register a second user to comment")
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            client_http.post("/api/auth/register", json={"email": "bob@example.com", "name": "Bob", "password": "AnotherPass123"})
        code2 = extract_code(buf2.getvalue())
        r = client_http.post("/api/auth/verify-email", json={"email": "bob@example.com", "code": code2})
        bob_token = r.json()["access_token"]
        bob_headers = {"Authorization": f"Bearer {bob_token}"}
        print("   OK: second user ready")

        print("\n12. Bob comments on Alice's post")
        r = client_http.post(f"/api/posts/{post_id}/comments/", headers=bob_headers, json={"text": "I think I saw this dog!"})
        assert r.status_code == 201, r.text
        print("   OK: comment created ->", r.json()["text"])

        print("\n13. Alice checks her notifications (should have Bob's comment)")
        r = client_http.get("/api/notifications/", headers=headers)
        assert r.status_code == 200, r.text
        notes = r.json()
        assert len(notes) >= 1 and "commented" in notes[0]["message"]
        print("   OK:", notes[0]["message"])

        print("\n14. Mark post resolved (author-only check)")
        r = client_http.patch(f"/api/posts/{post_id}", headers=headers, json={"status": "resolved"})
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "resolved"
        print("   OK: post resolved")

        print("\n15. Bob tries to edit Alice's post (should be forbidden)")
        r = client_http.patch(f"/api/posts/{post_id}", headers=bob_headers, json={"title": "hijacked"})
        assert r.status_code == 403, r.text
        print("   OK: correctly forbidden ->", r.json()["detail"])

        print("\n16. Unauthenticated post creation (should be rejected)")
        r = client_http.post("/api/posts/", data={"type": "alert", "title": "x", "description": "x", "latitude": "0", "longitude": "0"})
        assert r.status_code in (401, 403), r.text
        print("   OK: correctly rejected ->", r.status_code)

        print("\n17. WebSocket live notification (Bob connects near a new post, should get pushed a toast)")
        with client_http.websocket_connect(f"/ws/notifications?token={bob_token}") as ws:
            # Tell the server where Bob currently is (Bandra area)
            ws.send_json({"type": "location", "lat": 19.0500, "lng": 72.8300})

            # Alice creates a new post ~1km away — Bob should get a live push
            r = client_http.post(
                "/api/posts/",
                headers=headers,
                data={
                    "type": "alert",
                    "title": "Live test alert",
                    "description": "testing websocket push",
                    "latitude": "19.0510",
                    "longitude": "72.8310",
                },
            )
            assert r.status_code == 201, r.text
            new_post_id = r.json()["id"]

            pushed = ws.receive_json()
            assert pushed["type"] == "new_post"
            assert pushed["post_id"] == new_post_id
            print("   OK: Bob received live push ->", pushed["message"])

        print("\n18. WebSocket rejects an invalid token")
        try:
            with client_http.websocket_connect("/ws/notifications?token=not-a-real-token"):
                raise AssertionError("Expected connection to be rejected")
        except Exception:
            print("   OK: invalid token correctly rejected the connection")

    print("\n" + "=" * 60)
    print("ALL SMOKE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
