import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password
from app.models.models import User
from tests.conftest import client, TestingSessionLocal


def test_signup_success(test_db):
    """Test successful user registration"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["access_token"]
    assert data["user"]["email"] == "test@example.com"


def test_signup_duplicate_email(test_db):
    """Test signup with duplicate email"""
    # Create user first
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser1",
            "password": "password123"
        }
    )
    
    # Try to create user with same email
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_signin_success(test_db):
    """Test successful user signin"""
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    # Sign in
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_signin_invalid_password(test_db):
    """Test signin with invalid password"""
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    # Try to sign in with wrong password
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_forgot_password(test_db):
    """Test forgot password request"""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 200
    assert "If the email exists" in response.json()["message"]
