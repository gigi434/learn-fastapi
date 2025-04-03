from fastapi.testclient import TestClient
from fastapi import status

from TodoApp.main import app
from TodoApp.routers.todos import get_db, get_current_user
from TodoApp.models import Todos
from TodoApp.test.utils import override_get_db, override_get_current_user, TestingSessionLocal


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


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
