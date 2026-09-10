from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _to_out(n: Notification) -> NotificationOut:
    return NotificationOut(
        id=str(n.id),
        post_id=str(n.post_id),
        message=n.message,
        is_read=n.is_read,
        created_at=n.created_at,
    )


@router.get("/", response_model=List[NotificationOut])
async def list_notifications(current_user: User = Depends(get_current_user)):
    notes = (
        await Notification.find(Notification.user_id == current_user.id)
        .sort(-Notification.created_at)
        .limit(50)
        .to_list()
    )
    return [_to_out(n) for n in notes]


@router.get("/unread-count")
async def unread_count(current_user: User = Depends(get_current_user)):
    count = await Notification.find(
        Notification.user_id == current_user.id, Notification.is_read == False  # noqa: E712
    ).count()
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(notification_id: str, current_user: User = Depends(get_current_user)):
    note = await Notification.get(PydanticObjectId(notification_id))
    if not note or note.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found.")

    note.is_read = True
    await note.save()
    return _to_out(note)


@router.post("/read-all")
async def mark_all_read(current_user: User = Depends(get_current_user)):
    notes = await Notification.find(
        Notification.user_id == current_user.id, Notification.is_read == False  # noqa: E712
    ).to_list()
    for n in notes:
        n.is_read = True
        await n.save()
    return {"marked_read": len(notes)}
