from pydantic import BaseModel, ConfigDict


class CarImageOut(BaseModel):
    id: int
    car_id: int
    file_path: str
    file_name: str

    model_config = ConfigDict(from_attributes=True)
