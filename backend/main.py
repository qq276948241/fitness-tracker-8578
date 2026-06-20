from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from typing import List, Optional

from database import engine, get_db, Base
import models
import schemas
from auth import get_password_hash, verify_password, create_access_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="健身打卡 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_template_plans(db: Session):
    existing = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.is_template == 1).first()
    if existing:
        return

    templates = [
        {
            "name": "新手增肌计划",
            "description": "适合初学者的全身增肌训练，每周3次，每次45分钟",
            "plan_data": '{"frequency":3,"duration":45,"exercises":["深蹲","卧推","硬拉","引体向上","推举"],"level":"初级"}'
        },
        {
            "name": "减脂塑形计划",
            "description": "结合有氧和力量训练，高效燃脂塑形",
            "plan_data": '{"frequency":5,"duration":60,"exercises":["慢跑","波比跳","深蹲跳","俯卧撑","平板支撑"],"level":"中级"}'
        },
        {
            "name": "力量举计划",
            "description": "专注三大项力量提升，适合有基础的训练者",
            "plan_data": '{"frequency":4,"duration":90,"exercises":["深蹲","卧推","硬拉","推举","引体向上"],"level":"高级"}'
        },
        {
            "name": "居家徒手训练",
            "description": "无需器械，在家就能完成的全身训练",
            "plan_data": '{"frequency":4,"duration":30,"exercises":["俯卧撑","深蹲","平板支撑","卷腹","弓步蹲"],"level":"初级"}'
        },
        {
            "name": "HIIT 高强度间歇",
            "description": "短时间高强度训练，高效燃脂提升心肺",
            "plan_data": '{"frequency":3,"duration":25,"exercises":["波比跳","高抬腿","登山跑","开合跳","深蹲跳"],"level":"中级"}'
        }
    ]

    for t in templates:
        plan = models.WorkoutPlan(
            name=t["name"],
            description=t["description"],
            plan_data=t["plan_data"],
            is_template=1
        )
        db.add(plan)
    db.commit()


@app.on_event("startup")
def startup_event():
    db = next(get_db())
    init_template_plans(db)
    db.close()


@app.post("/api/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        height=user.height,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": user.username})
    return schemas.Token(access_token=access_token, user=schemas.UserResponse.model_validate(db_user))


@app.post("/api/auth/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return schemas.Token(access_token=access_token, user=schemas.UserResponse.model_validate(db_user))


@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.put("/api/auth/profile", response_model=schemas.UserResponse)
def update_profile(
    user_update: schemas.UserBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.full_name = user_update.full_name
    current_user.height = user_update.height
    current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/api/workouts", response_model=List[schemas.WorkoutRecordResponse])
def get_workouts(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    workout_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.WorkoutRecord).filter(models.WorkoutRecord.user_id == current_user.id)

    if start_date:
        query = query.filter(models.WorkoutRecord.date >= start_date)
    if end_date:
        query = query.filter(models.WorkoutRecord.date <= end_date)
    if workout_type:
        query = query.filter(models.WorkoutRecord.workout_type == workout_type)

    records = query.order_by(models.WorkoutRecord.date.desc()).offset(skip).limit(limit).all()
    return records


@app.post("/api/workouts", response_model=schemas.WorkoutRecordResponse)
def create_workout(
    workout: schemas.WorkoutRecordCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_workout = models.WorkoutRecord(
        user_id=current_user.id,
        date=workout.date,
        workout_type=workout.workout_type,
        duration=workout.duration,
        calories=workout.calories,
        notes=workout.notes,
        exercises=workout.exercises
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@app.get("/api/workouts/{workout_id}", response_model=schemas.WorkoutRecordResponse)
def get_workout(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutRecord).filter(
        models.WorkoutRecord.id == workout_id,
        models.WorkoutRecord.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="记录不存在")
    return workout


@app.put("/api/workouts/{workout_id}", response_model=schemas.WorkoutRecordResponse)
def update_workout(
    workout_id: int,
    workout_update: schemas.WorkoutRecordUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutRecord).filter(
        models.WorkoutRecord.id == workout_id,
        models.WorkoutRecord.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="记录不存在")

    workout.date = workout_update.date
    workout.workout_type = workout_update.workout_type
    workout.duration = workout_update.duration
    workout.calories = workout_update.calories
    workout.notes = workout_update.notes
    workout.exercises = workout_update.exercises

    db.commit()
    db.refresh(workout)
    return workout


@app.delete("/api/workouts/{workout_id}")
def delete_workout(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutRecord).filter(
        models.WorkoutRecord.id == workout_id,
        models.WorkoutRecord.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(workout)
    db.commit()
    return {"message": "删除成功"}


@app.get("/api/weight", response_model=List[schemas.WeightRecordResponse])
def get_weight_records(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.WeightRecord).filter(models.WeightRecord.user_id == current_user.id)

    if start_date:
        query = query.filter(models.WeightRecord.date >= start_date)
    if end_date:
        query = query.filter(models.WeightRecord.date <= end_date)

    records = query.order_by(models.WeightRecord.date.desc()).offset(skip).limit(limit).all()
    return records


@app.post("/api/weight", response_model=schemas.WeightRecordResponse)
def create_weight_record(
    weight: schemas.WeightRecordCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_weight = models.WeightRecord(
        user_id=current_user.id,
        date=weight.date,
        weight=weight.weight,
        body_fat=weight.body_fat,
        notes=weight.notes
    )
    db.add(db_weight)
    db.commit()
    db.refresh(db_weight)
    return db_weight


@app.put("/api/weight/{weight_id}", response_model=schemas.WeightRecordResponse)
def update_weight_record(
    weight_id: int,
    weight_update: schemas.WeightRecordUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    weight = db.query(models.WeightRecord).filter(
        models.WeightRecord.id == weight_id,
        models.WeightRecord.user_id == current_user.id
    ).first()
    if not weight:
        raise HTTPException(status_code=404, detail="记录不存在")

    weight.date = weight_update.date
    weight.weight = weight_update.weight
    weight.body_fat = weight_update.body_fat
    weight.notes = weight_update.notes

    db.commit()
    db.refresh(weight)
    return weight


@app.delete("/api/weight/{weight_id}")
def delete_weight_record(
    weight_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    weight = db.query(models.WeightRecord).filter(
        models.WeightRecord.id == weight_id,
        models.WeightRecord.user_id == current_user.id
    ).first()
    if not weight:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(weight)
    db.commit()
    return {"message": "删除成功"}


@app.get("/api/plans", response_model=List[schemas.WorkoutPlanResponse])
def get_workout_plans(
    include_templates: bool = True,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.WorkoutPlan).filter(
        (models.WorkoutPlan.user_id == current_user.id) |
        (models.WorkoutPlan.is_template == 1 if include_templates else False)
    )
    plans = query.order_by(models.WorkoutPlan.created_at.desc()).all()
    return plans


@app.post("/api/plans", response_model=schemas.WorkoutPlanResponse)
def create_workout_plan(
    plan: schemas.WorkoutPlanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_plan = models.WorkoutPlan(
        user_id=current_user.id,
        name=plan.name,
        description=plan.description,
        plan_data=plan.plan_data,
        is_template=0
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@app.get("/api/stats", response_model=schemas.StatsResponse)
def get_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workouts = db.query(models.WorkoutRecord).filter(
        models.WorkoutRecord.user_id == current_user.id
    ).all()

    weights = db.query(models.WeightRecord).filter(
        models.WeightRecord.user_id == current_user.id
    ).order_by(models.WeightRecord.date.asc()).all()

    total_workouts = len(workouts)
    total_duration = sum(w.duration or 0 for w in workouts)
    total_calories = sum(w.calories or 0 for w in workouts)

    workout_types = {}
    for w in workouts:
        if w.workout_type in workout_types:
            workout_types[w.workout_type] += 1
        else:
            workout_types[w.workout_type] = 1

    current_weight = weights[-1].weight if weights else None
    weight_change = (weights[-1].weight - weights[0].weight) if len(weights) >= 2 else None

    today = date.today()
    week_ago = today - timedelta(days=6)
    weekly_data = []
    for i in range(7):
        d = week_ago + timedelta(days=i)
        day_workouts = [w for w in workouts if w.date == d]
        weekly_data.append({
            "date": d.isoformat(),
            "count": len(day_workouts),
            "duration": sum(w.duration or 0 for w in day_workouts),
            "calories": sum(w.calories or 0 for w in day_workouts)
        })

    weight_history = [
        {"date": w.date.isoformat(), "weight": w.weight, "body_fat": w.body_fat}
        for w in weights
    ]

    return schemas.StatsResponse(
        total_workouts=total_workouts,
        total_duration=total_duration,
        total_calories=total_calories,
        current_weight=current_weight,
        weight_change=weight_change,
        workout_types=workout_types,
        weekly_data=weekly_data,
        weight_history=weight_history
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "健身打卡 API 运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
