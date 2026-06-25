from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, UploadFile, File, Query, Header
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
import logging
import uuid
import jwt
import bcrypt
import requests
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="STRATEX HABITAT API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("habitat")

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.environ["JWT_SECRET"]

# ---------------------------------------------------------------------------
# Object storage (Emergent managed)
# ---------------------------------------------------------------------------
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "stratex-habitat"
storage_key = None


def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key


def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(f"{STORAGE_URL}/objects/{path}",
                        headers={"X-Storage-Key": key, "Content-Type": content_type},
                        data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()


def get_object(path: str):
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")


MIME_TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif",
              "webp": "image/webp", "pdf": "application/pdf"}

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email,
               "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(key="access_token", value=token, httponly=True, secure=False,
                        samesite="lax", max_age=604800, path="/")


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(*roles):
    async def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions for this role")
        return user
    return checker


def now_iso():
    return datetime.now(timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
ROLES = ("homeowner", "contractor", "broker_admin", "reviewer", "executive")


class RegisterReq(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["homeowner", "contractor", "broker_admin", "reviewer", "executive"] = "homeowner"


class LoginReq(BaseModel):
    email: EmailStr
    password: str


class QuoteRequest(BaseModel):
    finding_id: Optional[str] = None
    title: str
    category: str
    description: Optional[str] = ""
    seriousness: Literal["low", "medium", "high", "urgent"] = "medium"
    target_timeframe: Optional[str] = "Flexible"
    desired_start: Optional[str] = None


class QuoteResponseReq(BaseModel):
    price_low: float
    price_high: float
    scope_notes: str
    timeline: str
    estimated_start: Optional[str] = None


class ReviewReq(BaseModel):
    contractor_id: str
    rating: int
    title: str
    body: str
    photos: List[str] = []


class FindingPatch(BaseModel):
    priority: Optional[str] = None
    seriousness: Optional[str] = None

# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------


@api_router.post("/auth/register")
async def register(body: RegisterReq, response: Response):
    email = body.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    uid = str(uuid.uuid4())
    doc = {"id": uid, "email": email, "password_hash": hash_password(body.password),
           "name": body.name, "role": body.role, "avatar": None, "created_at": now_iso()}
    await db.users.insert_one(doc)
    token = create_access_token(uid, email)
    set_auth_cookie(response, token)
    doc.pop("password_hash"); doc.pop("_id", None)
    return doc


@api_router.post("/auth/login")
async def login(body: LoginReq, response: Response):
    email = body.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user["id"], email)
    set_auth_cookie(response, token)
    user.pop("password_hash"); user.pop("_id", None)
    return user


@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}


@api_router.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return user

# ---------------------------------------------------------------------------
# Property / Twin / Assets
# ---------------------------------------------------------------------------


@api_router.get("/properties")
async def list_properties(user: dict = Depends(get_current_user)):
    q = {} if user["role"] in ("executive", "broker_admin", "reviewer") else {"owner_id": user["id"]}
    props = await db.properties.find(q, {"_id": 0}).to_list(100)
    return props


@api_router.get("/properties/{pid}")
async def get_property(pid: str, user: dict = Depends(get_current_user)):
    prop = await db.properties.find_one({"id": pid}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@api_router.get("/properties/{pid}/analytics")
async def get_analytics(pid: str, user: dict = Depends(get_current_user)):
    doc = await db.analytics.find_one({"property_id": pid}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="No analytics")
    return doc


@api_router.get("/properties/{pid}/assets")
async def list_assets(pid: str, user: dict = Depends(get_current_user)):
    return await db.assets.find({"property_id": pid}, {"_id": 0}).to_list(200)


@api_router.get("/assets/{aid}")
async def get_asset(aid: str, user: dict = Depends(get_current_user)):
    a = await db.assets.find_one({"id": aid}, {"_id": 0})
    if not a:
        raise HTTPException(status_code=404, detail="Asset not found")
    return a

# ---------------------------------------------------------------------------
# Findings / Maintenance / Insights
# ---------------------------------------------------------------------------


@api_router.get("/findings")
async def list_findings(property_id: Optional[str] = None, user: dict = Depends(get_current_user)):
    q = {}
    if property_id:
        q["property_id"] = property_id
    return await db.findings.find(q, {"_id": 0}).sort("created_at", -1).to_list(200)


@api_router.get("/findings/{fid}")
async def get_finding(fid: str, user: dict = Depends(get_current_user)):
    f = await db.findings.find_one({"id": fid}, {"_id": 0})
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    return f


@api_router.patch("/findings/{fid}")
async def patch_finding(fid: str, body: FindingPatch, user: dict = Depends(get_current_user)):
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")
    res = await db.findings.update_one({"id": fid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Finding not found")
    return await db.findings.find_one({"id": fid}, {"_id": 0})


@api_router.get("/maintenance")
async def list_maintenance(user: dict = Depends(get_current_user)):
    return await db.maintenance.find({}, {"_id": 0}).to_list(200)


@api_router.get("/insights")
async def list_insights(user: dict = Depends(get_current_user)):
    return await db.insights.find({}, {"_id": 0}).to_list(100)

# ---------------------------------------------------------------------------
# Quotes (procurement)
# ---------------------------------------------------------------------------


@api_router.get("/quotes")
async def list_quotes(user: dict = Depends(get_current_user)):
    if user["role"] == "contractor":
        q = {"contractor_responses.contractor_id": user["id"]}
        return await db.quotes.find(q, {"_id": 0}).sort("created_at", -1).to_list(200)
    q = {} if user["role"] in ("executive", "broker_admin") else {"owner_id": user["id"]}
    return await db.quotes.find(q, {"_id": 0}).sort("created_at", -1).to_list(200)


@api_router.post("/quotes")
async def create_quote(body: QuoteRequest, user: dict = Depends(require_role("homeowner"))):
    prop = await db.properties.find_one({"owner_id": user["id"]}, {"_id": 0})
    qid = str(uuid.uuid4())
    doc = {"id": qid, "owner_id": user["id"], "owner_name": user["name"],
           "property_id": prop["id"] if prop else None,
           "property_name": prop["name"] if prop else None,
           "finding_id": body.finding_id, "title": body.title, "category": body.category,
           "description": body.description, "seriousness": body.seriousness,
           "target_timeframe": body.target_timeframe, "desired_start": body.desired_start,
           "status": "open", "created_at": now_iso(),
           "contractor_responses": []}
    await db.quotes.insert_one(doc)
    # Auto-route to matching contractors as leads (mock brokerage routing)
    contractors = await db.contractors.find({"trades": body.category}, {"_id": 0, "id": 1}).to_list(50)
    routed = [c["id"] for c in contractors]
    await db.quotes.update_one({"id": qid}, {"$set": {"routed_to": routed}})
    doc["routed_to"] = routed
    doc.pop("_id", None)
    return doc


@api_router.get("/quotes/{qid}")
async def get_quote(qid: str, user: dict = Depends(get_current_user)):
    q = await db.quotes.find_one({"id": qid}, {"_id": 0})
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")
    return q


@api_router.post("/quotes/{qid}/respond")
async def respond_quote(qid: str, body: QuoteResponseReq, user: dict = Depends(require_role("contractor"))):
    q = await db.quotes.find_one({"id": qid})
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")
    contractor = await db.contractors.find_one({"owner_user_id": user["id"]}, {"_id": 0})
    resp = {"contractor_id": user["id"],
            "contractor_name": contractor["company_name"] if contractor else user["name"],
            "rating": contractor["public_rating"] if contractor else 0,
            "price_low": body.price_low, "price_high": body.price_high,
            "scope_notes": body.scope_notes, "timeline": body.timeline,
            "estimated_start": body.estimated_start, "created_at": now_iso()}
    await db.quotes.update_one({"id": qid}, {"$push": {"contractor_responses": resp},
                                             "$set": {"status": "responded"}})
    return await db.quotes.find_one({"id": qid}, {"_id": 0})

# ---------------------------------------------------------------------------
# Marketplace (contractor leads)
# ---------------------------------------------------------------------------


@api_router.get("/marketplace/leads")
async def marketplace_leads(user: dict = Depends(require_role("contractor", "broker_admin", "executive"))):
    if user["role"] == "contractor":
        profile = await db.contractors.find_one({"owner_user_id": user["id"]}, {"_id": 0, "id": 1})
        pid = profile["id"] if profile else "__none__"
        return await db.quotes.find({"routed_to": pid}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return await db.quotes.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)

# ---------------------------------------------------------------------------
# Contractors
# ---------------------------------------------------------------------------


@api_router.get("/contractors")
async def list_contractors(trade: Optional[str] = None, user: dict = Depends(get_current_user)):
    q = {"trades": trade} if trade else {}
    return await db.contractors.find(q, {"_id": 0}).sort("public_rating", -1).to_list(200)


@api_router.get("/contractors/{cid}")
async def get_contractor(cid: str, user: dict = Depends(get_current_user)):
    c = await db.contractors.find_one({"id": cid}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail="Contractor not found")
    reviews = await db.reviews.find({"contractor_id": cid}, {"_id": 0}).sort("created_at", -1).to_list(100)
    c["reviews"] = reviews
    return c


@api_router.post("/contractors")
async def upsert_contractor(body: dict, user: dict = Depends(require_role("contractor"))):
    existing = await db.contractors.find_one({"owner_user_id": user["id"]})
    fields = {k: body.get(k) for k in ["company_name", "description", "service_area", "license",
                                       "insurance", "website", "phone", "email", "trades", "logo",
                                       "job_photos", "external_testimonials"] if k in body}
    if existing:
        await db.contractors.update_one({"owner_user_id": user["id"]}, {"$set": fields})
        return await db.contractors.find_one({"owner_user_id": user["id"]}, {"_id": 0})
    cid = str(uuid.uuid4())
    doc = {"id": cid, "owner_user_id": user["id"], "company_name": body.get("company_name", user["name"]),
           "description": body.get("description", ""), "service_area": body.get("service_area", ""),
           "license": body.get("license", ""), "insurance": body.get("insurance", ""),
           "website": body.get("website", ""), "phone": body.get("phone", ""),
           "email": body.get("email", user["email"]), "trades": body.get("trades", []),
           "logo": body.get("logo"), "job_photos": body.get("job_photos", []),
           "external_testimonials": body.get("external_testimonials", []),
           "public_rating": 0.0, "verified_reviews": 0,
           "scorecard": {"performance_grade": "—", "external_confidence": 0, "responsiveness": 0,
                         "close_rate": 0, "satisfaction": 0, "compliance": 0},
           "created_at": now_iso()}
    await db.contractors.insert_one(doc)
    doc.pop("_id", None)
    return doc

# ---------------------------------------------------------------------------
# Reviews & Ratings
# ---------------------------------------------------------------------------


@api_router.get("/reviews")
async def list_reviews(contractor_id: Optional[str] = None, user: dict = Depends(get_current_user)):
    q = {"contractor_id": contractor_id} if contractor_id else {}
    return await db.reviews.find(q, {"_id": 0}).sort("created_at", -1).to_list(200)


@api_router.post("/reviews")
async def create_review(body: ReviewReq, user: dict = Depends(require_role("homeowner"))):
    rid = str(uuid.uuid4())
    doc = {"id": rid, "contractor_id": body.contractor_id, "author_id": user["id"],
           "author_name": user["name"], "rating": body.rating, "title": body.title,
           "body": body.body, "photos": body.photos, "source": "stratex_verified",
           "verified": True, "created_at": now_iso()}
    await db.reviews.insert_one(doc)
    # recompute public rating
    reviews = await db.reviews.find({"contractor_id": body.contractor_id, "source": "stratex_verified"}).to_list(500)
    avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0.0
    await db.contractors.update_one({"id": body.contractor_id},
                                    {"$set": {"public_rating": avg, "verified_reviews": len(reviews)}})
    doc.pop("_id", None)
    return doc

# ---------------------------------------------------------------------------
# Documents & Reports
# ---------------------------------------------------------------------------


@api_router.get("/documents")
async def list_documents(user: dict = Depends(get_current_user)):
    return await db.documents.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)


@api_router.get("/reports")
async def list_reports(user: dict = Depends(get_current_user)):
    return await db.reports.find({}, {"_id": 0}).sort("scan_date", -1).to_list(200)

# ---------------------------------------------------------------------------
# STRATEX Core handshake (mock publish / sync)
# ---------------------------------------------------------------------------


@api_router.get("/core/status")
async def core_status(user: dict = Depends(get_current_user)):
    last = await db.sync_log.find_one({}, {"_id": 0}, sort=[("ts", -1)])
    return {"connected": True, "engine": "STRATEX Core", "version": "2026.6",
            "last_sync": last["ts"] if last else None,
            "published_assets": await db.assets.count_documents({"published": True}),
            "pending": 0}


@api_router.post("/core/publish")
async def core_publish(user: dict = Depends(require_role("executive", "broker_admin", "reviewer"))):
    """Mock STRATEX Core publishing approved scans/reports into the shared property record."""
    ts = now_iso()
    await db.assets.update_many({}, {"$set": {"published": True, "published_at": ts}})
    await db.sync_log.insert_one({"id": str(uuid.uuid4()), "ts": ts, "by": user["id"],
                                  "action": "publish", "source": "stratex_core"})
    return {"ok": True, "ts": ts, "message": "Approved assets published to shared AWS property record"}

# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------


@api_router.post("/upload")
async def upload(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
    path = f"{APP_NAME}/uploads/{user['id']}/{uuid.uuid4()}.{ext}"
    data = await file.read()
    ctype = file.content_type or MIME_TYPES.get(ext, "application/octet-stream")
    result = put_object(path, data, ctype)
    await db.files.insert_one({"id": str(uuid.uuid4()), "storage_path": result["path"],
                               "original_filename": file.filename, "content_type": ctype,
                               "size": result.get("size", len(data)), "owner_id": user["id"],
                               "is_deleted": False, "created_at": now_iso()})
    backend = os.environ.get("REACT_APP_BACKEND_URL", "")
    return {"path": result["path"], "url": f"/api/files/{result['path']}"}


@api_router.get("/files/{path:path}")
async def download(path: str):
    record = await db.files.find_one({"storage_path": path, "is_deleted": False})
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    data, content_type = get_object(path)
    return Response(content=data, media_type=record.get("content_type", content_type))


@api_router.get("/")
async def root():
    return {"service": "STRATEX HABITAT", "status": "online"}

# ---------------------------------------------------------------------------
# App wiring
# ---------------------------------------------------------------------------
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True,
                   allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    try:
        init_storage()
        logger.info("Storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
    await seed_data()


@app.on_event("shutdown")
async def shutdown():
    client.close()

# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------
from seed import run_seed  # noqa: E402


async def seed_data():
    await run_seed(db, hash_password)
