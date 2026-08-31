import asyncio
import logging
from typing import Dict, Set, Optional, Any

logger = logging.getLogger("warehouse.sync_broadcast")

class SyncBroadcaster:
    def __init__(self):
        self.live_listeners: Dict[str, Set[asyncio.Queue]] = {}
        self.sim_listeners: Dict[int, Set[asyncio.Queue]] = {}
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def subscribe_live(self, warehouse_id: str, queue: asyncio.Queue):
        if warehouse_id not in self.live_listeners:
            self.live_listeners[warehouse_id] = set()
        self.live_listeners[warehouse_id].add(queue)
        logger.info("New live subscriber for warehouse %s", warehouse_id)

    def unsubscribe_live(self, warehouse_id: str, queue: asyncio.Queue):
        if warehouse_id in self.live_listeners:
            self.live_listeners[warehouse_id].discard(queue)
            if not self.live_listeners[warehouse_id]:
                del self.live_listeners[warehouse_id]
        logger.info("Unsubscribed live listener from warehouse %s", warehouse_id)

    def subscribe_sim(self, sim_run_id: int, queue: asyncio.Queue):
        if sim_run_id not in self.sim_listeners:
            self.sim_listeners[sim_run_id] = set()
        self.sim_listeners[sim_run_id].add(queue)
        logger.info("New simulation subscriber for run %s", sim_run_id)

    def unsubscribe_sim(self, sim_run_id: int, queue: asyncio.Queue):
        if sim_run_id in self.sim_listeners:
            self.sim_listeners[sim_run_id].discard(queue)
            if not self.sim_listeners[sim_run_id]:
                del self.sim_listeners[sim_run_id]
        logger.info("Unsubscribed simulation listener from run %s", sim_run_id)

    def broadcast_live(self, warehouse_id: str, event_data: dict):
        if warehouse_id not in self.live_listeners:
            return

        def _put():
            for q in list(self.live_listeners[warehouse_id]):
                try:
                    q.put_nowait(event_data)
                except Exception as e:
                    logger.warning("Failed to queue live event: %s", e)

        self._dispatch(_put)

    def broadcast_sim(self, sim_run_id: int, event_data: dict):
        if sim_run_id not in self.sim_listeners:
            return

        def _put():
            for q in list(self.sim_listeners[sim_run_id]):
                try:
                    q.put_nowait(event_data)
                except Exception as e:
                    logger.warning("Failed to queue sim event: %s", e)

        self._dispatch(_put)

    def broadcast_sync_event(self, warehouse_id: str, event_type: str, payload: dict = None):
        data = {"event_type": event_type, **(payload or {})}
        self.broadcast_live(warehouse_id, data)

    def _dispatch(self, func):
        if self.loop and self.loop.is_running():
            try:
                self.loop.call_soon_threadsafe(func)
                return
            except Exception:
                pass
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon(func)
        except RuntimeError:
            func()

broadcaster = SyncBroadcaster()
