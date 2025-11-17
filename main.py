import os
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CarOut(BaseModel):
    id: Optional[str] = None
    make: str
    model: str
    year: int
    price: float
    image: Optional[str] = None
    mileage: Optional[int] = None
    fuel: Optional[str] = None
    transmission: Optional[str] = None
    is_featured: bool = False


class BlogPostOut(BaseModel):
    id: Optional[str] = None
    title: str
    excerpt: Optional[str] = None
    content: str
    author: str
    cover_image: Optional[str] = None
    tags: Optional[list[str]] = []


@app.get("/")
def read_root():
    return {"message": "Car Dealership API is running"}


@app.get("/api/cars", response_model=List[CarOut])
def list_cars():
    try:
        docs = get_documents("car")
        cars = []
        for d in docs:
            # Normalize Mongo _id to string id
            item = {
                "id": str(d.get("_id")),
                "make": d.get("make"),
                "model": d.get("model"),
                "year": int(d.get("year", 2023)),
                "price": float(d.get("price", 0)),
                "image": d.get("image"),
                "mileage": d.get("mileage"),
                "fuel": d.get("fuel"),
                "transmission": d.get("transmission"),
                "is_featured": bool(d.get("is_featured", False)),
            }
            cars.append(item)
        return cars
    except Exception:
        # Fallback demo data if DB isn't configured
        return [
            {
                "id": "demo-1",
                "make": "Apex",
                "model": "GT-R Carbon",
                "year": 2024,
                "price": 124990,
                "image": "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?q=80&w=1600&auto=format&fit=crop",
                "mileage": 1200,
                "fuel": "Petrol",
                "transmission": "Automatic",
                "is_featured": True,
            },
            {
                "id": "demo-2",
                "make": "Voltera",
                "model": "E9 Performance",
                "year": 2025,
                "price": 89990,
                "image": "https://images.unsplash.com/photo-1542282088-fe8426682b8f?q=80&w=1600&auto=format&fit=crop",
                "mileage": 50,
                "fuel": "Electric",
                "transmission": "Single-Speed",
                "is_featured": True,
            },
            {
                "id": "demo-3",
                "make": "Lumine",
                "model": "S7 Avant",
                "year": 2023,
                "price": 74990,
                "image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1600&auto=format&fit=crop",
                "mileage": 8000,
                "fuel": "Hybrid",
                "transmission": "Automatic",
                "is_featured": False,
            },
        ]


@app.get("/api/blogs", response_model=List[BlogPostOut])
def list_blogs():
    try:
        docs = get_documents("blogpost")
        blogs = []
        for d in docs:
            blogs.append(
                {
                    "id": str(d.get("_id")),
                    "title": d.get("title"),
                    "excerpt": d.get("excerpt"),
                    "content": d.get("content", ""),
                    "author": d.get("author", "Team"),
                    "cover_image": d.get("cover_image"),
                    "tags": d.get("tags", []),
                }
            )
        return blogs
    except Exception:
        return [
            {
                "id": "b1",
                "title": "Designing the Future of Performance",
                "excerpt": "How aerodynamics and AI are redefining driving.",
                "content": "Long form content...",
                "author": "Editorial",
                "cover_image": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?q=80&w=1600&auto=format&fit=crop",
                "tags": ["design", "performance"],
            },
            {
                "id": "b2",
                "title": "Electric Thrill: Why EVs Are Exciting",
                "excerpt": "Torque, silence, and software-defined speed.",
                "content": "Long form content...",
                "author": "Editorial",
                "cover_image": "https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?q=80&w=1600&auto=format&fit=crop",
                "tags": ["ev", "innovation"],
            },
        ]


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
