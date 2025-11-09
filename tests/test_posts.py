import pytest
from tests.conftest import client


def get_auth_token(email: str = "test@example.com", username: str = "testuser",
                  password: str = "password123") -> str:
    """Helper to get authentication token"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "username": username,
            "password": password
        }
    )
    return response.json()["access_token"]


def test_create_post_success(test_db):
    """Test successful post creation"""
    token = get_auth_token()
    
    response = client.post(
        "/api/v1/posts",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "This is test content",
            "excerpt": "Test excerpt",
            "is_published": True,
            "tag_ids": []
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Post"


def test_get_post(test_db):
    """Test getting a post"""
    token = get_auth_token()
    
    # Create post
    create_response = client.post(
        "/api/v1/posts",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "Test content",
            "is_published": True,
            "tag_ids": []
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_response.json()["id"]
    
    # Get post
    response = client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["id"] == post_id


def test_list_posts(test_db):
    """Test listing posts"""
    response = client.get("/api/v1/posts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_post_success(test_db):
    """Test updating post by author"""
    token = get_auth_token()
    
    # Create post
    create_response = client.post(
        "/api/v1/posts",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "Test content",
            "is_published": False,
            "tag_ids": []
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_response.json()["id"]
    
    # Update post
    response = client.put(
        f"/api/v1/posts/{post_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_delete_post_success(test_db):
    """Test deleting post by author"""
    token = get_auth_token()
    
    # Create post
    create_response = client.post(
        "/api/v1/posts",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "Test content",
            "tag_ids": []
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_response.json()["id"]
    
    # Delete post
    response = client.delete(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204
