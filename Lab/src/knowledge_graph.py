import networkx as nx
try:
    from models import CarComponent, Symptom, Problem, MaintenanceTask, Entity
except ImportError:
    from src.models import CarComponent, Symptom, Problem, MaintenanceTask, Entity


class KnowledgeGraph:
    """Граф знаний для диагностики автомобилей."""

    def __init__(self):
        self.graph = nx.Graph()
        self._populate_graph()

    def _populate_graph(self):
        """Заполняет граф узлами и связями."""
        
        # ========== УЗЛЫ: КОМПОНЕНТЫ АВТОМОБИЛЯ (10+ узлов) ==========
        components = {
            "Двигатель": CarComponent("Двигатель", "Основной силовой агрегат", critical=True),
            "Тормозная система": CarComponent("Тормозная система", "Система безопасности", critical=True),
            "Подвеска": CarComponent("Подвеска", "Система амортизации", critical=False),
            "Масло": CarComponent("Масло двигателя", "Смазка и охлаждение", critical=True),
            "Колеса": CarComponent("Колеса", "Система движения", critical=True),
            "Аккумулятор": CarComponent("Аккумулятор", "Источник электроэнергии", critical=False),
            "Тормозные колодки": CarComponent("Тормозные колодки", "Элемент тормоза", critical=True),
            "Роторы": CarComponent("Роторы", "Диски тормозов", critical=True),
            "Амортизаторы": CarComponent("Амортизаторы", "Гасители колебаний", critical=False),
            "Фильтры": CarComponent("Фильтры", "Очистка системы", critical=False),
        }

        # ========== УЗЛЫ: СИМПТОМЫ (5+ узлов) ==========
        symptoms = {
            "Скрип": Symptom("Скрип", "высокая", ["Тормозная система", "Подвеска"]),
            "Вибрация": Symptom("Вибрация", "средняя", ["Колеса", "Роторы"]),
            "Стуки": Symptom("Стуки", "высокая", ["Подвеска", "Двигатель"]),
            "Запах": Symptom("Запах горелого", "высокая", ["Тормозные колодки", "Масло двигателя"]),
            "Слабый пуск": Symptom("Слабый пуск двигателя", "средняя", ["Аккумулятор", "Двигатель"]),
        }

        # ========== УЗЛЫ: ПРОБЛЕМЫ (5+ узлов) ==========
        problems = {
            "Износ тормозов": Problem("Износ тормозных колодок", "Излишний износ материала", 
                                      "Тормозная система", "замена"),
            "Дисбаланс": Problem("Дисбаланс колес", "Неточная балансировка", 
                                 "Колеса", "обслуживание"),
            "Утечка масла": Problem("Утечка масла", "Потеря рабочей жидкости", 
                                    "Двигатель", "диагностика"),
            "Люфт подвески": Problem("Люфт в подвеске", "Ослабление крепежей", 
                                      "Подвеска", "обслуживание"),
            "Слабый аккумулятор": Problem("Разряженный аккумулятор", "Недостаточная емкость", 
                                           "Аккумулятор", "замена"),
        }

        # ========== УЗЛЫ: ЗАДАЧИ ОБСЛУЖИВАНИЯ (5+ узлов) ==========
        tasks = {
            "ТО-1": MaintenanceTask("ТО-1 (10,000 км)", 10000, ["Масло двигателя", "Фильтры"], 
                                   "Замена масла и масляного фильтра"),
            "ТО-2": MaintenanceTask("ТО-2 (40,000 км)", 40000, ["Тормозная система", "Колеса"],
                                   "Проверка тормозной системы и балансировка колес"),
            "ТО-3": MaintenanceTask("ТО-3 (70,000 км)", 70000, ["Подвеска", "Амортизаторы"],
                                   "Осмотр подвески и замена амортизаторов"),
            "ТО-4": MaintenanceTask("ТО-4 (100,000 км)", 100000, ["Двигатель", "Коробка передач"],
                                   "Полная диагностика двигателя"),
            "ТО-5": MaintenanceTask("ТО-5 (Сезонное)", 0, ["Колеса", "Аккумулятор"],
                                   "Замена сезонной резины и проверка заряда"),
        }

        # Добавляю все узлы в граф
        for comp_name, comp in components.items():
            self.graph.add_node(comp_name, entity_type="component", obj=comp)
        for symp_name, symp in symptoms.items():
            self.graph.add_node(symp_name, entity_type="symptom", obj=symp)
        for prob_name, prob in problems.items():
            self.graph.add_node(prob_name, entity_type="problem", obj=prob)
        for task_name, task in tasks.items():
            self.graph.add_node(task_name, entity_type="task", obj=task)

        # ========== СВЯЗИ: СИМПТОМЫ ↔ КОМПОНЕНТЫ ==========
        # Скрип → Тормозная система
        self.graph.add_edge("Скрип", "Тормозная система", relation="может быть на")
        self.graph.add_edge("Скрип", "Подвеска", relation="может быть на")
        
        # Вибрация → Колеса
        self.graph.add_edge("Вибрация", "Колеса", relation="может быть на")
        self.graph.add_edge("Вибрация", "Роторы", relation="может быть на")
        
        # Стуки → Подвеска
        self.graph.add_edge("Стуки", "Подвеска", relation="может быть на")
        self.graph.add_edge("Стуки", "Двигатель", relation="может быть в")
        
        # Запах → Помогает диагностировать
        self.graph.add_edge("Запах горелого", "Тормозные колодки", relation="свидетельствует об износе")
        self.graph.add_edge("Запах горелого", "Масло двигателя", relation="указывает на проблему с")
        
        # Слабый пуск → Электричество
        self.graph.add_edge("Слабый пуск двигателя", "Аккумулятор", relation="вызван слабым")
        self.graph.add_edge("Слабый пуск двигателя", "Двигатель", relation="может быть в")

        # ========== СВЯЗИ: ПРОБЛЕМЫ ↔ КОМПОНЕНТЫ (ДИАГНОЗ) ==========
        self.graph.add_edge("Износ тормозных колодок", "Тормозные колодки", relation="проблема в")
        self.graph.add_edge("Износ тормозных колодок", "Тормозная система", relation="влияет на")
        
        self.graph.add_edge("Дисбаланс колес", "Колеса", relation="проблема в")
        
        self.graph.add_edge("Утечка масла", "Двигатель", relation="проблема в")
        self.graph.add_edge("Утечка масла", "Масло двигателя", relation="связана с")
        
        self.graph.add_edge("Люфт в подвеске", "Подвеска", relation="проблема в")
        self.graph.add_edge("Люфт в подвеске", "Амортизаторы", relation="может быть в")
        
        self.graph.add_edge("Разряженный аккумулятор", "Аккумулятор", relation="проблема в")

        # ========== СВЯЗИ: ЗАДАЧИ ТО ↔ КОМПОНЕНТЫ ==========
        self.graph.add_edge("ТО-1 (10,000 км)", "Масло двигателя", relation="замена на")
        self.graph.add_edge("ТО-1 (10,000 км)", "Фильтры", relation="замена на")
        
        self.graph.add_edge("ТО-2 (40,000 км)", "Тормозная система", relation="проверка")
        self.graph.add_edge("ТО-2 (40,000 км)", "Колеса", relation="балансировка")
        
        self.graph.add_edge("ТО-3 (70,000 км)", "Подвеска", relation="осмотр")
        self.graph.add_edge("ТО-3 (70,000 км)", "Амортизаторы", relation="замена на")
        
        self.graph.add_edge("ТО-4 (100,000 км)", "Двигатель", relation="полная диагностика")
        
        self.graph.add_edge("ТО-5 (Сезонное)", "Колеса", relation="замена на")
        self.graph.add_edge("ТО-5 (Сезонное)", "Аккумулятор", relation="проверка")

        # ========== СВЯЗИ: ПРОБЛЕМЫ ↔ ЗАДАЧИ ТО (РЕШЕНИЕ) ==========
        self.graph.add_edge("Износ тормозных колодок", "ТО-2 (40,000 км)", relation="решается в")
        self.graph.add_edge("Дисбаланс колес", "ТО-2 (40,000 км)", relation="решается в")
        self.graph.add_edge("Люфт в подвеске", "ТО-3 (70,000 км)", relation="решается в")
        self.graph.add_edge("Утечка масла", "ТО-4 (100,000 км)", relation="диагностируется в")
        self.graph.add_edge("Разряженный аккумулятор", "ТО-5 (Сезонное)", relation="проверяется в")

    def find_related_entities(self, node_name: str):
        """Находит все связанные сущности по одному узлу.
        
        Args:
            node_name: Название узла в графе
            
        Returns:
            dict с информацией об узле и его соседей с типами отношений
        """
        if node_name not in self.graph:
            return None

        node_data = self.graph.nodes[node_name]
        neighbors = self.graph.neighbors(node_name)

        result = {
            "node_name": node_name,
            "entity_type": node_data.get("entity_type"),
            "description": str(node_data.get("obj", "")),
            "related": []
        }

        for neighbor in neighbors:
            neighbor_data = self.graph.nodes[neighbor]
            edge_data = self.graph[node_name][neighbor]
            
            result["related"].append({
                "name": neighbor,
                "type": neighbor_data.get("entity_type"),
                "relation": edge_data.get("relation", "связана с"),
                "description": str(neighbor_data.get("obj", ""))
            })

        return result

    def get_all_nodes(self):
        """Возвращает все узлы графа сгруппированные по типам."""
        nodes_by_type = {
            "component": [],
            "symptom": [],
            "problem": [],
            "task": []
        }
        
        for node, data in self.graph.nodes(data=True):
            entity_type = data.get("entity_type")
            if entity_type in nodes_by_type:
                nodes_by_type[entity_type].append(node)
        
        return nodes_by_type

    def get_graph_stats(self):
        """Возвращает статистику графа."""
        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "nodes_by_type": self.get_all_nodes()
        }
