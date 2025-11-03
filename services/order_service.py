import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
if str(GEN) not in sys.path:
    sys.path.insert(0, str(GEN))

import os
import time
import uuid
from datetime import datetime, timezone
from concurrent import futures

import grpc
from google.protobuf import timestamp_pb2

from generated import order_pb2, order_pb2_grpc, user_pb2, user_pb2_grpc

USERSVC_ADDR = os.getenv("USERSVC_ADDR", "localhost:50051")


class InMemoryOrderRepo:
    def __init__(self):
        self.orders = {}

    def create(self, order_msg: order_pb2.Order):
        self.orders[order_msg.id] = order_msg
        return order_msg

    def get(self, oid: str):
        return self.orders.get(oid)

    def list(self, user_id: str | None = None):
        if user_id:
            return [o for o in self.orders.values() if o.user_id == user_id]
        return list(self.orders.values())


class OrderService(order_pb2_grpc.OrderServiceServicer):
    def __init__(self, repo: InMemoryOrderRepo, user_channel: grpc.Channel):
        self.repo = repo
        self.user_stub = user_pb2_grpc.UserServiceStub(user_channel)

    def _ensure_user(self, user_id: str) -> user_pb2.User:
        return self.user_stub.GetUser(user_pb2.GetUserRequest(id=user_id), timeout=2)

    def CreateOrder(self, request, context):
        if not request.user_id or not request.items or request.total <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "user_id, items and positive total are required")

        try:
            user = self._ensure_user(request.user_id)
        except grpc.RpcError as e:
            context.abort(e.code(), f"user lookup failed: {e.details()}")

        oid = str(uuid.uuid4())
        ts = timestamp_pb2.Timestamp()
        ts.FromDatetime(datetime.now(timezone.utc))
        order_msg = order_pb2.Order(
            id=oid,
            user_id=user.id,
            user_name_snapshot=user.name,
            items=list(request.items),
            total=request.total,
            created_at=ts,
        )
        self.repo.create(order_msg)
        return order_msg

    def GetOrder(self, request, context):
        order = self.repo.get(request.id)
        if not order:
            context.abort(grpc.StatusCode.NOT_FOUND, "order not found")
        return order

    def ListOrders(self, request, context):
        orders = self.repo.list(request.user_id if request.HasField("user_id") else None)
        return order_pb2.ListOrdersResponse(orders=orders)


def serve():
    for attempt in range(20):
        try:
            channel = grpc.insecure_channel(USERSVC_ADDR)
            grpc.channel_ready_future(channel).result(timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    else:
        raise RuntimeError(f"Could not connect to UserService at {USERSVC_ADDR}")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(InMemoryOrderRepo(), channel), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print(f"OrderService listening on :50052 (UserService at {USERSVC_ADDR})")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
