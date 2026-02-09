import streamlit as st
import networkx as nx
from knowledge_graph import KnowledgeGraph
from mock_data import car_data
from logic import check_rules
import plotly.graph_objs as go

st.set_page_config(page_title="🏎️ Диагностика авто: ЛР №2 & №3", layout="wide")

# ========== ИНИЦИАЛИЗАЦИЯ ГРАФА ==========
@st.cache_resource
def load_knowledge_graph():
    """Загружает граф знаний один раз."""
    return KnowledgeGraph()

kg = load_knowledge_graph()

# ========== ЗАГОЛОВОК ==========
st.title("🏎️ Система диагностики автомобилей")

# ========== СОЗДАНИЕ ВКЛАДОК ==========
tab1, tab2 = st.tabs(["📋 Регламент ТО", "🔗 Граф знаний"])

# ################################################################################
# ################################## ВКЛАДКА 1: ЛР №2 ###########################
# ################################################################################

with tab1:
    st.header("📋 Регламент планового обслуживания")
    st.write("Система диагностики на основе правил (Rule-Based System)")
    
    st.write("### Входные данные")

    col1, col2 = st.columns(2)
    
    with col1:
        mileage = st.number_input(
            "Пробег автомобиля (км)",
            value=car_data["mileage"],
            min_value=0,
            step=1000
        )

    with col2:
        is_diagnosed = st.checkbox(
            "Автомобиль прошел диагностику",
            value=car_data["is_diagnosed"]
        )

    # Выбор симптомов
    st.write("### Симптомы")
    available_symptoms = ["стучит", "скрип", "вибрация"]
    selected_symptoms = st.multiselect(
        "Выберите симптомы (если есть):",
        options=available_symptoms,
        default=car_data["symptoms"]
    )

    if st.button("🔍 Запустить диагностику", key="diagnosis_btn"):
        current_car = {
            "car_model": car_data["car_model"],
            "mileage": mileage,
            "symptoms": selected_symptoms,
            "is_diagnosed": is_diagnosed
        }

        result = check_rules(current_car)

        st.divider()
        st.write("### 📊 Результаты диагностики:")
        
        if "⛔️" in result:
            st.error(result)
        elif "✅" in result:
            st.success(result)
        else:
            st.warning(result)

# ################################################################################
# ################################## ВКЛАДКА 2: ЛР №3 ###########################
# ################################################################################

with tab2:
    st.header("🔗 Граф знаний: Объектная модель")
    st.write("Система на основе графа знаний (Knowledge Graph)")
    
    # ========== ВЫБОР УЗЛА ==========
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("⚙️ Выбор узла")

        
        # Тип узла
        all_nodes = kg.get_all_nodes()
        node_type_names = {
            "component": "🤖 Компоненты",
            "symptom": "🔔 Симптомы",
            "problem": "⚠️ Проблемы",
            "task": "📋 Задачи ТО"
        }

        selected_type = st.selectbox(
            "Тип сущности:",
            options=list(node_type_names.keys()),
            format_func=lambda x: node_type_names[x],
            key="tab2_type"
        )

        # Выбор узла
        available_nodes = all_nodes[selected_type]
        selected_node = st.selectbox(
            "Выберите узел:",
            options=available_nodes,
            key="tab2_node"
        )

        # Кнопка поиска
        search_button = st.button("🔍 Найти связи", key="tab2_search")

    # ========== ИНФОРМАЦИЯ ОБ УЗЛЕ ==========
    with col_right:
        st.subheader("📌 Информация об узле")
        
        if search_button or selected_node:
            result = kg.find_related_entities(selected_node)
            
            if result:
                st.markdown(f"**Название:** `{result['node_name']}`")
                st.markdown(f"**Тип:** `{node_type_names.get(result['entity_type'], result['entity_type'])}`")
                st.markdown(f"**Описание:**\n> {result['description']}")
                
                st.divider()
                st.subheader(f"🔗 Связанные сущности ({len(result['related'])})")
                
                if result['related']:
                    for idx, rel in enumerate(result['related'], 1):
                        with st.container(border=True):
                            col_icon, col_info = st.columns([0.1, 0.9])
                            
                            type_icons = {
                                "component": "🤖",
                                "symptom": "🔔",
                                "problem": "⚠️",
                                "task": "📋"
                            }
                            icon = type_icons.get(rel['type'], "🔗")
                            
                            with col_icon:
                                st.markdown(f"# {icon}")
                            
                            with col_info:
                                st.markdown(f"**{rel['name']}**")
                                st.caption(f"Отношение: *{rel['relation']}*")
                                st.text(rel['description'])
                else:
                    st.info("ℹ️ Связанных сущностей не найдено")
            else:
                st.warning("⚠️ Узел не найден в графе")

    # ========== ВИЗУАЛИЗАЦИЯ ГРАФА ==========
    st.divider()
    st.subheader("📊 Визуализация графа знаний")
    
    col_viz1, col_viz2 = st.columns([3, 1])
    
    with col_viz2:
        st.write("**Фильтры:**")
        viz_options = st.multiselect(
            "Показать типы:",
            options=["component", "symptom", "problem", "task"],
            default=["component", "symptom", "problem", "task"],
            format_func=lambda x: node_type_names[x],
            key="tab2_filter"
        )
    
    with col_viz1:
        # Фильтрация графа
        filtered_graph = kg.graph.copy()
        nodes_to_remove = []
        for node, data in filtered_graph.nodes(data=True):
            if data.get("entity_type") not in viz_options:
                nodes_to_remove.append(node)
        
        filtered_graph.remove_nodes_from(nodes_to_remove)
        
        # Создание Plotly визуализации
        pos = nx.spring_layout(filtered_graph, k=2, iterations=50, seed=42)
        
        # Подготовка рёбер
        edge_x = []
        edge_y = []
        for edge in filtered_graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        )
        
        # Подготовка узлов
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        color_map = {
            "component": "#FF6B6B",
            "symptom": "#4ECDC4",
            "problem": "#FFE66D",
            "task": "#95E1D3"
        }
        
        size_map = {
            "component": 20,
            "symptom": 15,
            "problem": 15,
            "task": 18
        }
        
        for node in filtered_graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            node_type = filtered_graph.nodes[node].get("entity_type")
            node_color.append(color_map.get(node_type, "#888"))
            node_size.append(size_map.get(node_type, 15))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )
        
        # Создание фигуры
        fig = go.Figure(data=[edge_trace, node_trace])
        
        fig.update_layout(
            title=f"Граф ({filtered_graph.number_of_nodes()} узлов, {filtered_graph.number_of_edges()} связей)",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#f0f0f0',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # ========== СТАТИСТИКА ==========
    st.divider()
    st.subheader("📈 Статистика графа")
    
    stats = kg.get_graph_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Узлов", stats["num_nodes"])
    with col2:
        st.metric("Связей", stats["num_edges"])
    with col3:
        st.metric("Компонентов", len(stats["nodes_by_type"]["component"]))
    with col4:
        st.metric("Задач ТО", len(stats["nodes_by_type"]["task"]))

st.divider()
