import streamlit as st
import networkx as nx
from knowledge_graph import KnowledgeGraph
import plotly.graph_objs as go
import plotly.express as px

st.set_page_config(page_title="Граф знаний: Диагностика авто", layout="wide")

# ========== ИНИЦИАЛИЗАЦИЯ ГРАФА ==========
@st.cache_resource
def load_knowledge_graph():
    """Загружает граф знаний один раз."""
    return KnowledgeGraph()

kg = load_knowledge_graph()

# ========== ЗАГОЛОВОК И ОПИСАНИЕ ==========
st.title("🏎️ Граф знаний: Диагностика автомобилей")
st.markdown("""
### Лабораторная работа №3: Объектная модель и Графы знаний

Этот интерфейс позволяет:
- 🔍 Исследовать **объекты** (компоненты, симптомы, проблемы, ТО)
- 🔗 Найти **связи** между элементами
- 📊 Визуализировать **граф знаний** системы диагностики
""")

# ========== ЛЕВАЯ ПАНЕЛЬ: ВЫБОР И ПОИСК ==========
st.sidebar.header("⚙️ Фильтры и выбор")

# Тип узла
all_nodes = kg.get_all_nodes()
node_type_names = {
    "component": "🤖 Компоненты",
    "symptom": "🔔 Симптомы",
    "problem": "⚠️ Проблемы",
    "task": "📋 Задачи ТО"
}

selected_type = st.sidebar.selectbox(
    "Тип сущности:",
    options=list(node_type_names.keys()),
    format_func=lambda x: node_type_names[x]
)

# Выбор узла из отфильтрованного списка
available_nodes = all_nodes[selected_type]
selected_node = st.sidebar.selectbox(
    "Выберите узел:",
    options=available_nodes,
    key="node_selector"
)

# Кнопка поиска
search_button = st.sidebar.button("🔍 Найти связи", width='stretch')

# ========== ГЛАВНАЯ ОБЛАСТЬ ==========
col1, col2 = st.columns([1, 1])

# ========== ЛЕВАЯ КОЛОНКА: ИНФОРМАЦИЯ О УЗЛЕ И СВЯЗЯХ ==========
with col1:
    st.subheader(f"📌 Информация об узле")
    
    if search_button or selected_node:
        result = kg.find_related_entities(selected_node)
        
        if result:
            # Информация об узле
            st.markdown(f"**Название:** `{result['node_name']}`")
            st.markdown(f"**Тип:** `{node_type_names.get(result['entity_type'], result['entity_type'])}`")
            st.markdown(f"**Описание:**\n> {result['description']}")
            
            st.divider()
            
            # Связанные сущности
            st.subheader(f"🔗 Связанные сущности ({len(result['related'])})")
            
            if result['related']:
                for idx, rel in enumerate(result['related'], 1):
                    with st.container(border=True):
                        col_icon, col_info = st.columns([0.15, 0.85])
                        
                        # Иконка типа
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

# ========== ПРАВАЯ КОЛОНКА: ВИЗУАЛИЗАЦИЯ ГРАФА ==========
with col2:
    st.subheader("📊 Визуализация графа")
    
    # Опции визуализации
    viz_options = st.multiselect(
        "Показать типы узлов:",
        options=["component", "symptom", "problem", "task"],
        default=["component", "symptom", "problem", "task"],
        format_func=lambda x: node_type_names[x],
        key="viz_filter"
    )
    
    # Фильтрация графа для визуализации
    filtered_graph = kg.graph.copy()
    nodes_to_remove = []
    for node, data in filtered_graph.nodes(data=True):
        if data.get("entity_type") not in viz_options:
            nodes_to_remove.append(node)
    
    filtered_graph.remove_nodes_from(nodes_to_remove)
    
    # Создание Plotly визуализации
    pos = nx.spring_layout(filtered_graph, k=2, iterations=50, seed=42)
    
    # Подготовка данных для Plotly
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
    
    # Узлы
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
        title=f"Граф знаний ({filtered_graph.number_of_nodes()} узлов, {filtered_graph.number_of_edges()} связей)",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#f0f0f0',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ========== НИЖНЯЯ ПАНЕЛЬ: СТАТИСТИКА ГРАФА ==========
st.divider()
st.subheader("📈 Статистика графа знаний")

stats = kg.get_graph_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Всего узлов", stats["num_nodes"])
with col2:
    st.metric("Всего связей", stats["num_edges"])
with col3:
    st.metric("Компонентов", len(stats["nodes_by_type"]["component"]))
with col4:
    st.metric("Задач ТО", len(stats["nodes_by_type"]["task"]))

# Детальная таблица
st.write("### Распределение узлов по типам")
type_data = {
    "Тип": [node_type_names[t] for t in ["component", "symptom", "problem", "task"]],
    "Количество": [
        len(stats["nodes_by_type"]["component"]),
        len(stats["nodes_by_type"]["symptom"]),
        len(stats["nodes_by_type"]["problem"]),
        len(stats["nodes_by_type"]["task"])
    ]
}

st.table(type_data)

# Footer
st.divider()
st.caption("""
**Разработано для ЛР №3 "Объектная модель и Графы знаний"**\n
Граф включает компоненты автомобиля, симптомы, проблемы и задачи обслуживания.
""")
