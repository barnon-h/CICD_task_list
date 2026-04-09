import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app( { "DATABASE" : ":memory:", "TESTING" : True })
    
    with app.app_context():
        from app.model import get_db
        db = get_db( app )
        with app.open_resource( "schema.sql" ) as f:
            db.executescript( f.read().decode( "utf8" ) )
    
    with app.test_client() as client:
        yield client

# Test Create task

def test_create_task( client ):
    response = client.post( "/tasks", json = { "title" : "Test Task", "description" : "This is a test task" } )
    assert response.status_code == 201
    data = response.get_json()
    assert data[ "title" ] == "Test Task"
    assert data[ "description" ] == "This is a test task"

def test_missing_title( client ):
    response = client.post( "/tasks", json = {} )
    assert response.status_code == 400

def test_empty_title( client ):
    response = client.post( "/tasks", json = { "title" : "   " } )
    assert response.status_code == 400

# Test Get tasks

def test_get_tasks( client ):
    client.post( "/tasks", json = { "title" : "Task 1" } )
    client.post( "/tasks", json = { "title" : "Task 2" } )

    response = client.get( "/tasks" )
    assert response.status_code == 200
    data = response.get_json()
    assert len( data ) == 2

def test_get_single_task( client ):
    response = client.post( "/tasks", json = { "title" : "Single Task" } )
    task_id = response.get_json()[ "id" ]

    response = client.get( f"/tasks/{task_id}" )
    assert response.status_code == 200
    data = response.get_json()
    assert data[ "title" ] == "Single Task"

def test_get_nonexistent_task( client ):
    response = client.get( "/tasks/999" )
    assert response.status_code == 404

def test_get_tasks_empty( client ):
    response = client.get( "/tasks" )
    assert response.status_code == 200
    data = response.get_json()
    assert len( data ) == 0

# Test Update Task

def test_update_task_title( client ):
    response = client.post( "/tasks", json = { "title" : "Old Title" } )
    task_id = response.get_json()[ "id" ]

    response = client.put( f"/tasks/{task_id}", json = { "title" : "New Title" } )
    assert response.status_code == 200
    data = response.get_json()
    assert data[ "title" ] == "New Title"

def test_update_task_completed( client ):
    response = client.post( "/tasks", json = { "title" : "Incomplete Task" } )
    task_id = response.get_json()[ "id" ]

    response = client.put( f"/tasks/{task_id}", json = { "completed" : True } )
    assert response.status_code == 200
    data = response.get_json()
    assert data[ "completed" ] == True


def test_update_nonexistent_task( client ):
    response = client.put( "/tasks/999", json = { "title" : "Doesn't Exist" } )
    assert response.status_code == 404

# Test Delete Task

def test_delete_task( client ):
    response = client.post( "/tasks", json = { "title" : "Task to Delete" } )
    task_id = response.get_json()[ "id" ]

    response = client.delete( f"/tasks/{task_id}" )
    assert response.status_code == 204

    response = client.get( f"/tasks/{task_id}" )
    assert response.status_code == 404

def test_delete_nonexistent_task( client ):
    response = client.delete( "/tasks/999" )
    assert response.status_code == 404