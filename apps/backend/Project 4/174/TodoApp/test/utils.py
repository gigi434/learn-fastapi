import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from TodoApp.database import Base
from TodoApp.models import Users, Todos
import pytest
from sqlalchemy import text

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
