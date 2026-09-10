from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut
from app.services.ws_manager import manager

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: str, payload: CommentCreate, current_user: User = Depends(get_current_user)
):
    post = await Post.get(PydanticObjectId(post_id))
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found.")

    comment = Comment(post_id=post.id, author_id=current_user.id, text=payload.text)
    await comment.insert()

    if post.author_id != current_user.id:
        message = f'{current_user.name} commented on your post "{post.title}"'
        note = await Notification(
            user_id=post.author_id, post_id=post.id, message=message
        ).insert()
        await manager.send_to_user(
            str(post.author_id),
            {"type": "new_comment", "post_id": str(post.id), "message": note.message},
        )

    return CommentOut(
        id=str(comment.id),
        post_id=str(comment.post_id),
        author_id=str(comment.author_id),
        author_name=current_user.name,
        text=comment.text,
        created_at=comment.created_at,
    )


@router.get("/", response_model=List[CommentOut])
async def list_comments(post_id: str):
    comments = (
        await Comment.find(Comment.post_id == PydanticObjectId(post_id))
        .sort(+Comment.created_at)
        .to_list()
    )
    results = []
    for c in comments:
        author = await User.get(c.author_id)
        results.append(
            CommentOut(
                id=str(c.id),
                post_id=str(c.post_id),
                author_id=str(c.author_id),
                author_name=author.name if author else "Unknown",
                text=c.text,
                created_at=c.created_at,
            )
        )
    return results
