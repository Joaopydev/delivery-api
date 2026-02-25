import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.ai.client import AIClient
from app.services.orders.OrderService import OrderService
from app.db.models.schemas import OrderStatus, Order
from app.repository.order_repository import OrderRepository


class ReadyTimeEstimationService:

    SYSTEM_PROMPT = """
        You are an assistant that adjusts preparation time estimates for a delivery kitchen.

        Rules:
        - Use ONLY the provided data
        - Do NOT invent information
        - Return ONLY valid JSON
        - The JSON must contain the key "extra_minutes"
        - "extra_minutes" must be an integer ('can be zero')
        - Do not add any text outside the JSON
    """

    def __init__(self, session):

        self.client = AIClient()
        self.order_repository = OrderRepository(session=session)
        self.order_service = OrderService(order_repository=self.order_repository)
    
    async def estimate(self, target_order: Dict[str, Any]) -> datetime:

        orders = await self.order_service.list_orders(order_status=OrderStatus.COMPLETED)
        average_minutes = self._calculate_average_preparation_time(orders=orders)

        payload = {
            "orders_in_preparation": [order.to_dict for order in orders],
            "average_preparation_minutes": average_minutes,
            "target_order": target_order
        }
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": self.user_prompt(payload)},
        ]
        raw_response = json.loads(self.client.chat(messages=messages))

        return self._calculate_final_estimated_time(
            target_order=target_order,
            base_minutes=average_minutes,
            extra_minutes=raw_response["extra_minutes"]
        )
    
    def _calculate_average_preparation_time(
        self,
        orders: List[Order]
    ) -> int:

        durations = []

        for order in orders:
            if order.confirmed_on and order.order_ready_in:
                delta = order.order_ready_in - order.confirmed_on
                durations.append(delta.total_seconds() / 60)

        if not durations:
            return 40
        
        return int(sum(durations) / len(durations))
    
    def _calculate_final_estimated_time(
        self,
        target_order: Dict[str, Any],
        base_minutes: int,
        extra_minutes: int
    ) -> datetime:
        
        total_minutes = base_minutes + extra_minutes
        return target_order["confirmed_on"] + timedelta(minutes=total_minutes)

    def user_prompt(self, payload: Dict[str, Any]) -> str:
        
        return f"""
            Current kitchen data and orders (in JSON):
            {json.dumps(payload, default=str, ensure_ascii=False)}
            
            Based on the complexity of the target order and the current kitchen load,
            return how many EXTRA minutes should be added to the average preparation time.
        """