from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

class SimulatedLocation:
    def __init__(self, location_id: str, x: float, y: float, location_type: str):
        self.id = location_id
        self.x = x
        self.y = y
        self.location_type = location_type  # e.g., STORAGE | PACKING | CHARGING


class SimulatedGridCell:
    def __init__(self, x: int, y: int, traversable: bool, cost: float, cell_type: str):
        self.x = x
        self.y = y
        self.traversable = traversable
        self.cost = cost
        self.cell_type = cell_type  # e.g., NORMAL | RESTRICTED | HIGH_RISK


class SimulatedObstacle:
    def __init__(self, obstacle_id: int, x: int, y: int, width: int, height: int):
        self.id = obstacle_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class SimulatedRobot:
    def __init__(
        self,
        robot_id: int,
        robot_code: str,
        warehouse_id: str,
        x: float,
        y: float,
        status: str = "AVAILABLE",
        battery_level: float = 100.0,
        max_payload: float = 150.0,
        max_speed: float = 1.0
    ):
        self.id = robot_id
        self.robot_code = robot_code
        self.warehouse_id = warehouse_id
        self.current_x = x
        self.current_y = y
        self.status = status
        self.battery_level = battery_level
        self.max_payload = max_payload
        self.max_speed = max_speed

        # Assignment
        self.assigned_task_id: Optional[int] = None
        self.target_location_id: Optional[str] = None
        self.target_x: Optional[float] = None
        self.target_y: Optional[float] = None

        # Routing & Movement
        self.active_path: List[Tuple[int, int]] = []
        self.path_cost: float = 0.0
        self.wait_ticks: int = 0

        # Metrics trackers
        self.total_distance: float = 0.0
        self.travel_time: float = 0.0
        self.idle_time: float = 0.0
        self.waiting_time: float = 0.0
        self.charging_time: float = 0.0
        self.completed_tasks: int = 0
        self.failed_tasks: int = 0
        self.replans: int = 0
        self.conflicts: int = 0


class SimulatedTask:
    def __init__(
        self,
        task_id: int,
        task_number: str,
        warehouse_id: str,
        task_type: str,
        product_id: str,
        source_location_id: str,
        destination_location_id: str,
        requested_quantity: int,
        priority: str = "MEDIUM",
        priority_score: int = 10,
        order_id: Optional[str] = None
    ):
        self.id = task_id
        self.task_number = task_number
        self.warehouse_id = warehouse_id
        self.task_type = task_type
        self.product_id = product_id
        self.source_location_id = source_location_id
        self.destination_location_id = destination_location_id
        self.requested_quantity = requested_quantity
        self.priority = priority
        self.priority_score = priority_score
        self.order_id = order_id
        
        self.status = "QUEUED"  # QUEUED | ASSIGNED | IN_PROGRESS | COMPLETED | FAILED
        self.assigned_robot_id: Optional[str] = None
        
        # Timing trackers (in simulation minutes/ticks)
        self.created_at_sim: float = 0.0
        self.started_at_sim: Optional[float] = None
        self.completed_at_sim: Optional[float] = None
        self.failed_at_sim: Optional[float] = None


class SimulatedOrder:
    def __init__(
        self,
        order_id: str,
        customer_ref: str,
        warehouse_id: str,
        status: str = "CREATED",
        priority: str = "MEDIUM"
    ):
        self.id = order_id
        self.customer_ref = customer_ref
        self.warehouse_id = warehouse_id
        self.status = status  # CREATED | VALIDATED | RESERVED | PICKING | PACKING | SHIPPED | COMPLETED
        self.priority = priority
        self.items: List[Dict[str, Any]] = []  # list of {item_id, requested_qty}
        
        # Timing trackers (in simulation minutes/ticks)
        self.created_at_sim: float = 0.0
        self.completed_at_sim: Optional[float] = None
