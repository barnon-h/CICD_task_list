from flask import Blueprint, current_app, request, jsonify
from .model import get_db

logic_bp = Blueprint( 'logic',  __name__ )

# Response codes
SUCCESS = 200
CREATED = 201
ERROR = 400
NOT_FOUND = 404

def to_dict( row ):
    return {
        "id" : row[ 'id' ],
        "title" : row[ "title"],
        "description" : row[ 'description' ],
        "completed" : bool( row[ 'completed' ]),
        "created_at" : row[ 'created_at' ]
    }

##### Crud Operations #####

# Create new task
@logic_bp.route( "/tasks", methods = [ "POST" ] )
def create_tasks():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify( { "error" : "Title is required" } ), ERROR

    title = data[ "title" ].strip()
    description = data["description" ].strip() if "description" in data else ""

    if not title:
        return jsonify( { "error" : "Title cannot be empty" } ), ERROR

    db = get_db( current_app )
    cursor = db.cursor()

    cursor.execute( "INSERT INTO tasks ( title, description ) VALUES ( ?, ? )", ( title, description ) )
    db.commit()

    row = db.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid, )).fetchone()
    db.close()

    return jsonify( to_dict( row ) ), CREATED

# Get all tasks
@logic_bp.route( "/tasks", methods = [ "GET" ])
def get_tasks():
    db = get_db( current_app )
    rows = db.execute( "SELECT * FROM tasks ORDER BY created_at DESC" ).fetchall()

    db.close()
    return jsonify( [ to_dict( row ) for row in rows ] ), SUCCESS

# Get single task
@logic_bp.route( "/tasks/<int:task_id>", methods = [ "GET" ])
def get_task( task_id ):
    db = get_db( current_app )
    row = db.execute( "SELECT * FROM tasks WHERE id = ?", ( task_id, ) ).fetchone()
    db.close()

    if row:
        return jsonify( to_dict( row ) ), SUCCESS
    else:
        return jsonify( { "error" : "Task not found" } ), NOT_FOUND

# Update task
@logic_bp.route("/tasks/<int:task_id>", methods = ["PUT", "GET", "DELETE"])
def update_task( task_id ):
    data = request.get_json()

    if not data:
        return jsonify( { "error" : "No data provided" } ), ERROR

    db = get_db( current_app )
    row = db.execute( "SELECT * FROM tasks WHERE id = ?", ( task_id, ) ).fetchone()

    if not row:
        db.close()
        return jsonify( { "error" : "Task not found" } ), NOT_FOUND

    title = data.get( "title", row[ "title" ] ).strip()
    description = data.get( "description", row[ "description" ] ).strip()
    completed = int( data.get( "completed", row[ "completed" ] ) )

    if not title:
        db.close()
        return jsonify( { "error" : "Title cannot be empty" } ), ERROR

    db.execute(
        "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
        ( title, description, completed, task_id )
    )
    db.commit()
    row = db.execute( "SELECT * FROM tasks WHERE id = ?", ( task_id, ) ).fetchone()
    db.close()

    return jsonify( to_dict( row ) ), SUCCESS

# Delete task
@logic_bp.route( "/tasks/<int:task_id>", methods = [ "DELETE" ])
def delete_task( task_id ):
    db = get_db( current_app )
    row = db.execute( "SELECT * FROM tasks WHERE id = ?", ( task_id, ) ).fetchone()

    if not row:
        db.close()
        return jsonify( { "error" : "Task not found" } ), NOT_FOUND

    db.execute( "DELETE FROM tasks WHERE id = ?", ( task_id, ) )
    db.commit()
    db.close()

    return jsonify( { "message" : "Task deleted successfully" } ), SUCCESS