from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from database import supabase

# Initialize FastAPI app
app = FastAPI()

# Root route to test Supabase connection
@app.get("/")
def test_connection():
    response = supabase.table("tasks").select("*").execute()
    return {"status": "Connected!", "data": response.data}

# Define a Task model
class Task(BaseModel):
    title: str
    completed: bool 

# Create a new task
@app.post("/tasks/")
def create_task(task: Task):
    data = {"title": task.title, "completed": task.completed}
    response = supabase.table("tasks").insert(data).execute()
    
    if response.data:
        return {"message": "Task added!", "task": response.data[0]}
    else:
        raise HTTPException(status_code=500, detail="Failed to add task")

# Get all tasks
@app.get("/tasks/")
def get_tasks():
    response = supabase.table("tasks").select("*").execute()
    return response.data or []

# Get a specific task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    response = supabase.table("tasks").select("*").eq("id", task_id).execute()
    
    if response.data:
        return response.data[0]  # Return first task found
    else:
        raise HTTPException(status_code=404, detail="Task not found")

# Update a task (including toggling `completed`)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    response = supabase.table("tasks").update(updated_task.dict()).eq("id", task_id).execute()

    if response.data:
        return {"message": "Task updated!", "task": response.data[0]}
    else:
        raise HTTPException(status_code=404, detail="Task not found or no changes made")

# Toggle the completed status of a task
@app.patch("/tasks/{task_id}/toggle")
def toggle_task_completion(task_id: int):
    # Get the current task state
    task_response = supabase.table("tasks").select("completed").eq("id", task_id).execute()
    
    if not task_response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    current_status = task_response.data[0]["completed"]
    new_status = not current_status  # Toggle True/False

    # Update the task
    response = supabase.table("tasks").update({"completed": new_status}).eq("id", task_id).execute()
    
    if response.data:
        return {"message": "Task completion status toggled!", "task": response.data[0]}
    else:
        raise HTTPException(status_code=500, detail="Failed to toggle task status")

# Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    response = supabase.table("tasks").delete().eq("id", task_id).execute()
    
    if response.data:
        return {"message": "Task deleted successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

# Run FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
