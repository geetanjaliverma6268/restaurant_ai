from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.ai_brain import analyze_order
from backend.database import create_tables, get_db, Order as DBOrder
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Restaurant AI")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/app")
async def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("frontend/dashboard.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Tables banao startup pe
@app.on_event("startup")
async def startup():
    create_tables()
    print("Database ready! ✅")

MENU = {
    "burger": 120,
    "pizza": 250,
    "pasta": 180,
    "cold drink": 50,
    "fries": 80,
    "sandwich": 100
}

class OrderRequest(BaseModel):
    text: str

@app.get("/")
async def home():
    return {"message": "Restaurant AI chal raha hai! 🍕"}

@app.get("/menu")
async def get_menu():
    return {"menu": MENU}

@app.post("/order")
async def receive_order(order: OrderRequest, db: Session = Depends(get_db)):
    # AI se analyze karo
    ai_response = analyze_order(order.text)
    
    try:
        order_data = json.loads(ai_response)
        
        # Database mein save karo
        db_order = DBOrder(
            customer_text=order.text,
            items=",".join(order_data.get("items", [])),
            quantities=",".join(map(str, order_data.get("quantities", []))),
            total=order_data.get("total", 0),
            message=order_data.get("message", ""),
            status="received"
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        return {
            "status": "success",
            "order_id": db_order.id,
            "order": order_data
        }
    except:
        return {
            "status": "success",
            "message": ai_response
        }

@app.get("/orders")
async def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(DBOrder).order_by(DBOrder.created_at.desc()).all()
    return {
        "total_orders": len(orders),
        "orders": [
            {
                "id": o.id,
                "customer_text": o.customer_text,
                "items": o.items,
                "total": o.total,
                "status": o.status,
                "time": str(o.created_at)
            }
            for o in orders
        ]
    }

@app.put("/orders/{order_id}/status")
async def update_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(DBOrder).filter(DBOrder.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        return {"message": f"Order {order_id} status updated to {status}"}
    return {"error": "Order not found"}