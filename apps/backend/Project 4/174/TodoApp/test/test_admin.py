from TodoApp.test.utils import override_get_db, override_get_current_user, test_todo
from TodoApp.routers.admin import get_db, get_current_user
from TodoApp.main import app
from fastapi.testclient import TestClient
from fastapi import status
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_admin_read_all_users_authenticated(test_todo):
    '''
    adminがすべてのtodoを取得するテスト
    '''
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1,
                                'title': "Test Todo",
                                'description': "Test Description",
                                'priority': 5,
                                'complete': False,
                                'owner_id': 1}]
