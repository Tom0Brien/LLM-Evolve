from typing import Dict, Type, List, Optional
from src.tasks.base import AbstractBaseTask

class TaskRegistry:
    _registry: Dict[str, Type[AbstractBaseTask]] = {}

    @classmethod
    def register(cls, task_cls: Type[AbstractBaseTask]):
        """Decorator to register a task class."""
        pass

    @classmethod
    def register_task(cls, name_override: str = None):
        def decorator(task_cls):
            # If name not provided, use lowercased class name (minus 'Task')
            name = name_override
            if not name:
                name = task_cls.__name__.lower().replace("task", "")
            
            cls._registry[name] = task_cls
            return task_cls
        return decorator

    @classmethod
    def get_task(cls, name: str) -> Optional[AbstractBaseTask]:
        """Get a task instance by name."""
        task_cls = cls._registry.get(name.lower())
        if task_cls:
            return task_cls()
        return None

    @classmethod
    def list_tasks(cls) -> List[str]:
        """List all registered task names."""
        return sorted(list(cls._registry.keys()))

# Global instance not strictly needed if using classmethods, but for imports:
register_task = TaskRegistry.register_task
get_task = TaskRegistry.get_task
list_tasks = TaskRegistry.list_tasks
