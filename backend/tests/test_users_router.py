import pytest
from fastapi.testclient import TestClient
from app import crud, schemas, models


class TestUsersRouter:
    def test_read_users_as_super_admin(self, client: TestClient, db):
        """Test getting all users as super admin."""
        # Create a super admin user
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Create regular users
        for i in range(3):
            user_data = schemas.UserCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="password",
                is_super_admin=False,
            )
            crud.create_user(db, user_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Get all users
        response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 4  # 3 regular users + 1 super admin

    def test_read_users_as_regular_user_forbidden(self, client: TestClient, db):
        """Test that regular users cannot get all users."""
        # Create a regular user
        user_data = schemas.UserCreate(
            name="Regular User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login as regular user
        login_response = client.post(
            "/auth/login", json={"email": "user@example.com", "password": "password"}
        )
        token = login_response.json()["access_token"]

        # Try to get all users (should fail)
        response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_read_users_pagination(self, client: TestClient, db):
        """Test users pagination."""
        # Create a super admin user
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Create multiple users
        for i in range(10):
            user_data = schemas.UserCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="password",
                is_super_admin=False,
            )
            crud.create_user(db, user_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Test pagination
        response = client.get(
            "/users/?skip=2&limit=3", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 3

    def test_read_user_own_profile(self, client: TestClient, db):
        """Test that users can read their own profile."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/auth/login", json={"email": "user@example.com", "password": "password"}
        )
        token = login_response.json()["access_token"]

        # Read own profile
        response = client.get(
            f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["id"] == user.id
        assert user_data["email"] == user.email

    def test_read_user_other_profile_as_regular_user_forbidden(
        self, client: TestClient, db
    ):
        """Test that regular users cannot read other users' profiles."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Login as user1
        login_response = client.post(
            "/auth/login", json={"email": "user1@example.com", "password": "password"}
        )
        token = login_response.json()["access_token"]

        # Try to read user2's profile (should fail)
        response = client.get(
            f"/users/{user2.id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

    def test_read_user_other_profile_as_super_admin(self, client: TestClient, db):
        """Test that super admin can read any user's profile."""
        # Create a super admin
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Create regular user
        user_data = schemas.UserCreate(
            name="Regular User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Read user's profile
        response = client.get(
            f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["id"] == user.id

    def test_read_user_not_found(self, client: TestClient, db):
        """Test reading non-existent user."""
        # Create a super admin
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Try to read non-existent user
        response = client.get(
            "/users/nonexistent-id", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_update_user_own_profile(self, client: TestClient, db):
        """Test that users can update their own profile."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/auth/login", json={"email": "user@example.com", "password": "password"}
        )
        token = login_response.json()["access_token"]

        # Update own profile
        update_data = {"name": "Updated Name"}
        response = client.put(
            f"/users/{user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["name"] == "Updated Name"

    def test_update_user_other_profile_as_regular_user_forbidden(
        self, client: TestClient, db
    ):
        """Test that regular users cannot update other users' profiles."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Login as user1
        login_response = client.post(
            "/auth/login", json={"email": "user1@example.com", "password": "password"}
        )
        token = login_response.json()["access_token"]

        # Try to update user2's profile (should fail)
        update_data = {"name": "Hacked Name"}
        response = client.put(
            f"/users/{user2.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_update_user_super_admin_status_as_regular_user_forbidden(
        self, client: TestClient, db
    ):
        """Test that regular users cannot modify super admin status."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/auth/login", json={"email": "user@example.com", "password": "password"}
        )
        token = login_response.json()["access_token"]

        # Try to make themselves super admin (should fail)
        update_data = {"is_super_admin": True}
        response = client.put(
            f"/users/{user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_update_user_super_admin_status_as_super_admin(
        self, client: TestClient, db
    ):
        """Test that super admin can modify super admin status."""
        # Create a super admin
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Create regular user
        user_data = schemas.UserCreate(
            name="Regular User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Make user super admin
        update_data = {"is_super_admin": True}
        response = client.put(
            f"/users/{user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["is_super_admin"] is True

    def test_update_user_not_found(self, client: TestClient, db):
        """Test updating non-existent user."""
        # Create a super admin
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Try to update non-existent user
        update_data = {"name": "New Name"}
        response = client.put(
            "/users/nonexistent-id",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_delete_user_as_super_admin(self, client: TestClient, db):
        """Test deleting a user as super admin."""
        # Create a super admin
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Create regular user
        user_data = schemas.UserCreate(
            name="Regular User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Delete user
        response = client.delete(
            f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"

    def test_delete_user_as_regular_user_forbidden(self, client: TestClient, db):
        """Test that regular users cannot delete users."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Login as user1
        login_response = client.post(
            "/auth/login", json={"email": "user1@example.com", "password": "password"}
        )
        token = login_response.json()["access_token"]

        # Try to delete user2 (should fail)
        response = client.delete(
            f"/users/{user2.id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

    def test_delete_user_not_found(self, client: TestClient, db):
        """Test deleting non-existent user."""
        # Create a super admin
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        # Login as super admin
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Try to delete non-existent user
        response = client.delete(
            "/users/nonexistent-id", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_unauthorized_access(self, client: TestClient):
        """Test that all endpoints require authentication."""
        # Test without token
        response = client.get("/users/")
        assert response.status_code == 401

        response = client.get("/users/some-id")
        assert response.status_code == 401

        response = client.put("/users/some-id", json={"name": "New Name"})
        assert response.status_code == 401

        response = client.delete("/users/some-id")
        assert response.status_code == 401

    def test_invalid_token(self, client: TestClient):
        """Test that invalid tokens are rejected."""
        # Test with invalid token
        invalid_token = "invalid.jwt.token"

        response = client.get(
            "/users/", headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == 401
