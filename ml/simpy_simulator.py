import random
import logging
from typing import Dict, Any

logger = logging.getLogger("warehouse.simpy")

simpy_available = False
try:
    import simpy
    simpy_available = True
    logger.info("SimPy discrete-event simulation library successfully imported.")
except ImportError:
    logger.warning("SimPy not available in Python environment. Running discrete simulation in rule-based mock mode.")


class PackingStationWarehouseSimulation:
    def __init__(self, env, num_operators: int, mean_packing_time: float):
        self.env = env
        # Resource represents the operators available for packing
        self.operator_resource = simpy.Resource(env, capacity=num_operators)
        self.mean_packing_time = mean_packing_time
        
        # Performance trackers
        self.wait_times = []
        self.packing_times = []
        self.queue_lengths = []
        
    def pack_order(self, order_name: str):
        """Simulates the packing process for a single order."""
        arrival_time = self.env.now
        
        # Track active queue size prior to request
        self.queue_lengths.append(len(self.operator_resource.queue))
        
        # Request an operator
        with self.operator_resource.request() as request:
            yield request
            
            # Operator is now assigned
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)
            
            # Packing duration modeled as exponential distribution
            packing_duration = random.expovariate(1.0 / self.mean_packing_time)
            self.packing_times.append(packing_duration)
            
            yield self.env.timeout(packing_duration)


def order_generator(env, warehouse: PackingStationWarehouseSimulation, arrival_interval: float, rng: random.Random = None):
    """Generates order arrivals at a conveyor belt destination zone."""
    _rng = rng or random
    order_id = 1
    while True:
        # Wait for next order arrival (modeled as Poisson process)
        yield env.timeout(_rng.expovariate(1.0 / arrival_interval))
        env.process(warehouse.pack_order(f"ORD-{order_id:03d}"))
        order_id += 1


def run_simpy_experiment(
    duration: float = 480.0, # 8 hour shift (in minutes)
    num_operators: int = 3, 
    mean_arrival_interval: float = 5.0, # order every 5 minutes
    mean_packing_time: float = 12.0, # takes 12 minutes to pack an order
    random_seed: int = None  # Optional seed for reproducibility
) -> Dict[str, Any]:
    """Runs a discrete-event queueing simulation experiment and returns statistics."""
    # Create a dedicated Random instance for deterministic reproducibility
    rng = random.Random(random_seed) if random_seed is not None else random.Random()
    
    if not simpy_available:
        # Fallback Mock Statistics
        logger.info("Running mock SimPy queueing simulation...")
        return {
            "status": "mock",
            "experiment_duration_minutes": duration,
            "operators_count": num_operators,
            "random_seed": random_seed,
            "orders_processed": 94,
            "average_queue_wait_minutes": 18.5,
            "average_packing_time_minutes": 11.8,
            "operator_utilization_pct": 82.5,
            "max_queue_bottleneck": 6
        }
        
    # Setup SimPy environment
    env = simpy.Environment()
    warehouse = PackingStationWarehouseSimulation(env, num_operators, mean_packing_time)
    
    # Monkey-patch the pack_order to use the seeded RNG for packing duration
    original_pack_order = warehouse.pack_order
    def seeded_pack_order(order_name: str):
        arrival_time = env.now
        warehouse.queue_lengths.append(len(warehouse.operator_resource.queue))
        with warehouse.operator_resource.request() as request:
            yield request
            wait_time = env.now - arrival_time
            warehouse.wait_times.append(wait_time)
            packing_duration = rng.expovariate(1.0 / warehouse.mean_packing_time)
            warehouse.packing_times.append(packing_duration)
            yield env.timeout(packing_duration)
    warehouse.pack_order = seeded_pack_order
    
    # Register order arrival generator process with seeded RNG
    env.process(order_generator(env, warehouse, mean_arrival_interval, rng))
    
    # Execute simulation
    env.run(until=duration)
    
    # Calculate performance metrics
    orders_processed = len(warehouse.packing_times)
    avg_wait = sum(warehouse.wait_times) / len(warehouse.wait_times) if warehouse.wait_times else 0.0
    avg_pack = sum(warehouse.packing_times) / len(warehouse.packing_times) if warehouse.packing_times else 0.0
    max_queue = max(warehouse.queue_lengths) if warehouse.queue_lengths else 0
    
    # Calculate Utilization: total operational minutes spent / (operators * total duration)
    total_packing_duration = sum(warehouse.packing_times)
    utilization = (total_packing_duration / (num_operators * duration)) * 100
    utilization = min(utilization, 100.0) # Cap at 100%
    
    return {
        "status": "success",
        "experiment_duration_minutes": duration,
        "operators_count": num_operators,
        "random_seed": random_seed,
        "orders_processed": orders_processed,
        "average_queue_wait_minutes": round(avg_wait, 2),
        "average_packing_time_minutes": round(avg_pack, 2),
        "operator_utilization_pct": round(utilization, 2),
        "max_queue_bottleneck": max_queue
    }


if __name__ == "__main__":
    # Test script run
    results = run_simpy_experiment()
    print("Discrete Simulation Results:")
    print(results)
