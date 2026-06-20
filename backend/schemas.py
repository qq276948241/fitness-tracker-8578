from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    height: Optional[float] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class WorkoutRecordBase(BaseModel):
    date: date
    workout_type: str
    duration: Optional[int] = None
    calories: Optional[int] = None
    notes: Optional[str] = None
    exercises: Optional[str] = None


class WorkoutRecordCreate(WorkoutRecordBase):
    pass


class WorkoutRecordUpdate(WorkoutRecordBase):
    pass


class WorkoutRecordResponse(WorkoutRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WeightRecordBase(BaseModel):
    date: date
    weight: float
    body_fat: Optional[float] = None
    notes: Optional[str] = None


class WeightRecordCreate(WeightRecordBase):
    pass


class WeightRecordUpdate(WeightRecordBase):
    pass


class WeightRecordResponse(WeightRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    plan_data: Optional[str] = None


class WorkoutPlanCreate(WorkoutPlanBase):
    pass


class WorkoutPlanUpdate(WorkoutPlanBase):
    pass


class WorkoutPlanResponse(WorkoutPlanBase):
    id: int
    user_id: Optional[int] = None
    is_template: int
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_workouts: int
    total_duration: int
    total_calories: int
    current_weight: Optional[float] = None
    weight_change: Optional[float] = None
    workout_types: dict
    weekly_data: List[dict]
    weight_history: List[dict]
