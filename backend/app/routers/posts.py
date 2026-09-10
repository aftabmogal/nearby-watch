from datetime import datetime, timezone
from typing import List, Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.config import settings
from app.core.deps import get_current_user
from app.models.notification import Notification
from app.models.post import GeoJSONPoint, Post
from app.models.user import User
from app.schemas.post import PostOut, PostUpdate
from app.services.storage import save_file
from app.services.ws_manager import manager

router = APIRouter(prefix="/posts", tags=["posts"])

VALID_TYPES = {"lost_pet", "lost_item", "found_item", "alert"}


async def _to_post_out(post: Post, distance_km: Optional[float] = None) -> PostOut:
    author = await User.get(post.author_id)
    return PostOut(
        id=str(post.id),
        author_id=str(post.author_id),
        author_name=author.name if author else "Unknown",
        type=post.type,
        title=post.title,
        description=post.description,
        photos=post.photos,
        latitude=post.location.coordinates[1],
        longitude=post.location.coordinates[0],
        address_label=post.address_label,
        status=post.status,
        report_count=post.report_count,
        created_at=post.created_at,
        resolved_at=post.resolved_at,
        distance_km=round(distance_km, 2) if distance_km is not None else None,
    )


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    type: str = Form(...),
    title: str = Form(..., min_length=1, max_length=150),
    description: str = Form(..., min_length=1, max_length=2000),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    address_label: Optional[str] = Form(None),
    photos: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_user),
):
    if type not in VALID_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid post type '{type}'.")

    real_photos = [p for p in photos if p.filename]
    if len(real_photos) > settings.MAX_PHOTOS_PER_POST:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Maximum {settings.MAX_PHOTOS_PER_POST} photos allowed.",
        )

    photo_urls = []
    for photo in real_photos:
        try:
            photo_urls.append(await save_file(photo))
        except ValueError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

    post = Post(
        author_id=current_user.id,
        type=type,
        title=title,
        description=description,
        photos=photo_urls,
        location=GeoJSONPoint(coordinates=[longitude, latitude]),
        address_label=address_label,
    )
    await post.insert()

    # Live-notify nearby connected users, then persist a Notification record
    # for whoever was actually matched so they still see it in their
    # notification list even if they weren't looking at the screen.
    message = f"New {type.replace('_', ' ')} nearby: {title}"
    matched_user_ids = await manager.broadcast_near(
        latitude,
        longitude,
        settings.NOTIFY_RADIUS_KM,
        {"type": "new_post", "post_id": str(post.id), "message": message},
        exclude_user_id=str(current_user.id),
    )
    for uid in matched_user_ids:
        await Notification(
            user_id=PydanticObjectId(uid), post_id=post.id, message=message
        ).insert()

    return await _to_post_out(post)


@router.get("/nearby", response_model=List[PostOut])
async def nearby_posts(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5, gt=0, le=100),
    type: Optional[str] = Query(None),
    status_filter: str = Query("active", alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    if type and type not in VALID_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid post type '{type}'.")

    mongo_query: dict = {
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius_km * 1000,  # metres
            }
        },
        "status": status_filter,
    }
    if type:
        mongo_query["type"] = type

    posts = await Post.find(mongo_query).skip(skip).limit(limit).to_list()

    results = []
    for p in posts:
        d = manager._haversine_km(lat, lng, p.location.coordinates[1], p.location.coordinates[0])
        results.append(await _to_post_out(p, d))
    return results


@router.get("/mine/list", response_model=List[PostOut])
async def my_posts(current_user: User = Depends(get_current_user)):
    posts = await Post.find(Post.author_id == current_user.id).sort(-Post.created_at).to_list()
    return [await _to_post_out(p) for p in posts]


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: str):
    post = await Post.get(PydanticObjectId(post_id))
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found.")
    return await _to_post_out(post)


@router.patch("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: str, payload: PostUpdate, current_user: User = Depends(get_current_user)
):
    post = await Post.get(PydanticObjectId(post_id))
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found.")
    if post.author_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized to edit this post.")

    if payload.title is not None:
        post.title = payload.title
    if payload.description is not None:
        post.description = payload.description
    if payload.status is not None:
        post.status = payload.status
        post.resolved_at = datetime.now(timezone.utc) if payload.status == "resolved" else None

    await post.save()
    return await _to_post_out(post)


@router.post("/{post_id}/report", response_model=PostOut)
async def report_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await Post.get(PydanticObjectId(post_id))
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found.")

    post.report_count += 1
    await post.save()
    return await _to_post_out(post)
