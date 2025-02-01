from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from .. import schemas
from ..cruds import setting_crud
from ..database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/setting",
    tags=["setting"]
)

@router.get("/automatic-sending", response_model=schemas.SettingAutomaticSendingResponse)
def get_setting(db: Session = Depends(get_db)):
    return setting_crud.get_automatic_sending(db)

@router.post("/toggle-automatic-sending", response_model=schemas.BaseModel)
def toggle_automatic_sending(db: Session = Depends(get_db)):
    return setting_crud.toggle_automatic_sending(db)

@router.post("/toggle-media-resolution-by-seed", response_model=schemas.BaseModel)
def toggle_media_resolution(seed: schemas.ToggleMediaResolution, db: Session = Depends(get_db)):
    return setting_crud.toggle_media_resolution_by_seed(seed=seed.seed, db=db)

@router.post("/media-resolution-by-seed", response_model=schemas.ToggleMediaResolutionResponse)
def toggle_media_resolution(seed: schemas.ToggleMediaResolution, db: Session = Depends(get_db)):
    return setting_crud.get_media_resolution_by_seed(seed=seed.seed, db=db)