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
    return Users(id=1, username="testuser", email="test@example.com", hashed_password="fakepassword", is_active=True, role="admin")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    '''
    todoオブジェクトを作成してテストケースに提供するジェネレーター
    '''
    # テスト用のtodoオブジェクトを作成する
    todo = Todos(id=1, title="Test Todo",
                 description="Test Description", priority=5, complete=False, owner_id=1)
    # テスト用のデータベースセッションを作成する
    db = TestingSessionLocal()
    # テスト用のtodoオブジェクトをデータベースに追加する
    db.add(todo)
    # データベースの変更をコミットする
    db.commit()

    # テストケースにtodoオブジェクトを提供する　例：test_read_all_todos_authenticated(test_todo)　のtest_todo
    yield todo
    # テスト終了後にtodosテーブルのすべてのデータを削除してテスト環境をクリーンアップする
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()


def test_read_all_todos_authenticated(test_todo):
    '''
    認証されたユーザーがすべてのtodoを取得するテスト
    '''
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1,
                                'title': "Test Todo",
                                'description': "Test Description",
                                'priority': 5,
                                'complete': False,
                                'owner_id': 1}]


def test_read_one_todos_authenticated(test_todo):
    '''
    存在するtodoのidを指定した場合、200エラーが返されることを確認する
    '''
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'id': 1,
                               'title': "Test Todo",
                               'description': "Test Description",
                               'priority': 5,
                               'complete': False,
                               'owner_id': 1}


def test_read_one_todos_not_found():
    '''
    存在しないtodoのidを指定した場合、404エラーが返されることを確認する
    '''
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo(test_todo):
    '''
    新しいtodoを作成するテスト
    '''
    request_data = {
        "title": "New Todo",
        "description": "New Description",
        "priority": 3,
        "complete": False
    }
    response = client.post("/todo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    # idが1のレコードは既に作成されているため、idが2のレコードが作成される
    todo_model = db.query(Todos).filter(Todos.id == 2).first()
    assert todo_model is not None
    assert todo_model.title == "New Todo"
    assert todo_model.description == "New Description"
    assert todo_model.priority == 3
    assert todo_model.complete == False


def test_update_todo(test_todo):
    '''
    既存のtodoを更新した場合、204ステータスコードが返されることを確認する
    '''
    request_data = {
        "title": "Updated Todo",
        "description": "Updated Description",
        "priority": 2,
        "complete": True
    }
    response = client.put("/todo/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo_model = db.query(Todos).filter(Todos.id == 1).first()
    assert todo_model is not None
    assert todo_model.title == "Updated Todo"
    assert todo_model.description == "Updated Description"
    assert todo_model.priority == 2
    assert todo_model.complete == True


def test_update_todo_not_found(test_todo):
    '''
    存在しないtodoのidを更新しようとした場合、404エラーが返されることを確認する
    '''
    request_data = {
        "title": "Updated Todo",
        "description": "Updated Description",
        "priority": 2,
        "complete": True
    }
    response = client.put("/todo/999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(test_todo):
    '''
    既存のtodoを削除した場合、204ステータスコードが返されることを確認する
    '''
    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo_model = db.query(Todos).filter(Todos.id == 1).first()
    assert todo_model is None


def test_delete_todo_not_found(test_todo):
    '''
    存在しないtodoのidを削除しようとした場合、404エラーが返されることを確認する
    '''
    response = client.delete("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}
