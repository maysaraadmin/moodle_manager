from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="Sample FastAPI Application",
    description="A sample FastAPI application for testing the FastAPI Manager GUI",
    version="1.0.0"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data models
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

# In-memory storage (for demo purposes)
items_db = []
users_db = []

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2023-01-01T00:00:00Z"}

@app.get("/items", response_model=List[Item])
async def get_items():
    """Get all items"""
    return items_db

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    """Create a new item"""
    items_db.append(item)
    return item

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get item by ID"""
    if item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """Update an item"""
    if item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return item

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item"""
    if item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    deleted_item = items_db.pop(item_id)
    return {"message": "Item deleted", "item": deleted_item}

@app.get("/users", response_model=List[User])
async def get_users():
    """Get all users"""
    return users_db

@app.post("/users", response_model=User)
async def create_user(user: User):
    """Create a new user"""
    users_db.append(user)
    return user

@app.get("/info")
async def get_info():
    """Get application information"""
    return {
        "name": "Sample FastAPI App",
        "version": "1.0.0",
        "endpoints": [
            "/",
            "/health",
            "/items",
            "/items/{item_id}",
            "/users",
            "/info",
            "/docs",
            "/openapi.json"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("sample_app:app", host="127.0.0.1", port=8000, reload=True)
