import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import status
import pytest

from TodoApp.database import Base
from TodoApp.main import app
from TodoApp.routers.todos import get_db, get_current_user
from TodoApp.models import Todos, Users

# Determine the absolute path to the database file based on the location of this file
BASE_DIR = Path(__file__).resolve().parent
SQLALCHEMY_DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "testdb.db")}'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       'check_same_thread': False}, poolclass=StaticPool)


# テスト用のデータベースセッションを作成するためのセッションファクトリを設定
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

# データベースのテーブルを作成する
Base.metadata.create_all(bind=engine)


def override_get_db():
    """既存のget_db関数を上書きして、テスト用のモックを使用する関数"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_user():
    """既存のget_current_user関数を上書きして、テスト用のモックを使用する関数"""
    return Users(id=1, username="testuser", email="test@example.com", hashed_password="fakepassword", is_active=True)


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(id=1, title="Test Todo",
                 description="Test Description", priority=5, complete=False, owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    # todoオブジェクトを返す
    yield todo
    # テスト終了後にtodosテーブルのすべてのデータを削除してテスト環境をクリーンアップする
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()


def test_read_all_todos_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1,
                                'title': "Test Todo",
                                'description': "Test Description",
                                'priority': 5,
                                'complete': False,
                                'owner_id': 1}]
