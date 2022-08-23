from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..oauth2 import getCurrentUser
from ..schemas import *

BASE_PATH = Path(__file__).resolve().parent

router = APIRouter(tags=["Tracker"])

templates = Jinja2Templates(
    directory=str(BASE_PATH) + "/../templates/", autoescape=False, auto_reload=True
)


@router.get("/")
def homePage(request: Request, db: Session = Depends(get_db)):
    whens = db.query(models.Log).order_by(models.Log.when.desc())
    return templates.TemplateResponse(
        "index.html", context={"request": request, "whens": whens}
    )


@router.post("/", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND)
async def createLog(request: Request, db: Session = Depends(get_db)):
    req = await request.form()
    req = {"when": req["date"]}
    new_log = models.Log(**dict(req))

    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return request.url_for("view", log_id=new_log.id)


@router.get("/add", status_code=status.HTTP_200_OK)
def addPage(request: Request, db: Session = Depends(get_db)):
    foods = db.query(models.Food).order_by(models.Food.created_at.desc()).all()
    return templates.TemplateResponse(
        "add.html", context={"request": request, "foods": foods, "food": None}
    )


@router.post("/add", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND)
async def addFood(request: Request, db: Session = Depends(get_db)):
    req = await request.form()
    id = req["food-id"]
    if id:
        food_q = db.query(models.Food).filter_by(id=int(id))
        req = await request.form()
        req = {
            "food_name": req["food-name"],
            "proteins": req["protein"],
            "carbs": req["carbohydrates"],
            "fats": req["fat"],
        }

        food_q.update(req, synchronize_session=False)
    else:
        req = {
            "food_name": req["food-name"],
            "proteins": req["protein"],
            "carbs": req["carbohydrates"],
            "fats": req["fat"],
        }
        new_food = models.Food(**dict(req))
        db.add(new_food)

    db.commit()
    return request.url_for("addPage")


@router.get("/del/{food_id}", response_class=RedirectResponse)
def deleteById(request: Request, food_id: int, db: Session = Depends(get_db)):
    food_q = db.query(models.Food).filter_by(id=food_id)
    food_q.delete(synchronize_session=False)
    db.commit()
    return request.url_for("addPage")


@router.get(
    "/edit/{food_id}", response_class=RedirectResponse, status_code=status.HTTP_200_OK
)
def updateById(request: Request, food_id: int, db: Session = Depends(get_db)):
    foods = db.query(models.Food).order_by(models.Food.created_at.desc()).all()
    food = db.query(models.Food).filter_by(id=food_id).first()

    return templates.TemplateResponse(
        "add.html", context={"request": request, "foods": foods, "food": food}
    )


@router.get("/view/{log_id}", response_class=RedirectResponse)
def view(request: Request, log_id: int, db: Session = Depends(get_db)):
    foods = db.query(models.Food).order_by(models.Food.food_name.asc()).all()
    log = db.query(models.Log).filter_by(id=log_id).first()
    totals = {"proteins": 0, "carbs": 0, "fats": 0, "calories": 0}

    for food in log.foods:
        totals["proteins"] += food.proteins
        totals["carbs"] += food.carbs
        totals["fats"] += food.fats
        totals["calories"] += food.calories

    return templates.TemplateResponse(
        "view.html",
        context={"request": request, "log": log,
                 "foods": foods, "totals": totals},
    )


@router.post("/log/{log_id}", response_class=RedirectResponse)
async def addFoodLog(request: Request, log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.Log).filter_by(id=log_id).first()
    req = await request.form()
    food = db.query(models.Food).filter_by(id=int(req["food-select"])).first()
    log.foods.append(food)
    db.commit()
    return RedirectResponse(
        url=f"/food/view/{log_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/rlog/{log_id}/{food_id}",)
def removeFoodLog(request: Request, log_id: int, food_id: int, db: Session = Depends(get_db)):
    log = db.query(models.Log).filter_by(id=log_id).first()
    food = db.query(models.Food).filter_by(id=food_id).first()

    log.foods.remove(food)
    db.commit()
    return RedirectResponse(
        url=f"/food/view/{log_id}", status_code=status.HTTP_303_SEE_OTHER
    )
