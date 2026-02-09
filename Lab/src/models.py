from dataclasses import dataclass, field
from typing import List


@dataclass
class CarComponent:
    """Компонент автомобиля."""
    name: str
    description: str
    critical: bool = False

    def __str__(self):
        status = "🔴 КРИТИЧНА" if self.critical else "🟡 Важна"
        return f"[{status}] {self.name}: {self.description}"


@dataclass
class Symptom:
    """Симптом проблемы в автомобиле."""
    name: str
    severity: str  # "низкая", "средняя", "высокая"
    related_components: List[str] = field(default_factory=list)

    def __str__(self):
        severity_emoji = {"низкая": "🟢", "средняя": "🟡", "высокая": "🔴"}
        emoji = severity_emoji.get(self.severity, "⚪")
        return f"{emoji} {self.name} (тяжесть: {self.severity})"


@dataclass
class Problem:
    """Диагностируемая проблема."""
    name: str
    description: str
    affected_component: str
    repair_type: str  # "замена", "обслуживание", "диагностика"

    def __str__(self):
        repair_emoji = {"замена": "🔄", "обслуживание": "🔧", "диагностика": "🔍"}
        emoji = repair_emoji.get(self.repair_type, "⚙️")
        return f"{emoji} {self.name} ({self.affected_component})"


@dataclass
class MaintenanceTask:
    """Задача планового обслуживания."""
    name: str
    mileage_interval: int  # км
    components: List[str] = field(default_factory=list)
    description: str = ""

    def __str__(self):
        return f"📋 {self.name} (через {self.mileage_interval} км) для: {', '.join(self.components)}"


@dataclass
class Entity:
    """Базовая сущность для узла графа знаний."""
    entity_type: str  # "component", "symptom", "problem", "task"
    name: str
    description: str = ""

    def __str__(self):
        return f"[{self.entity_type}] {self.name}"
