import streamlit as st
from mock_data import car_data
from logic import check_rules

st.title("🚗 Диагностика автомобиля — Rule-Based System")

st.write("### Входные данные")

mileage = st.sidebar.number_input(
    "Пробег автомобиля (км)",
    value=car_data["mileage"]
)

is_diagnosed = st.sidebar.checkbox(
    "Автомобиль прошел диагностику",
    value=car_data["is_diagnosed"]
)

if st.button("Запустить диагностику"):
    current_car = {
        "car_model": car_data["car_model"],
        "mileage": mileage,
        "symptoms": car_data["symptoms"],
        "is_diagnosed": is_diagnosed
    }

    result = check_rules(current_car)

    if "⛔️" in result:
        st.error(result)
    elif "✅" in result:
        st.success(result)
    else:
        st.warning(result)
