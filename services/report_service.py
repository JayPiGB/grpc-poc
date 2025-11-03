import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
if str(GEN) not in sys.path:
    sys.path.insert(0, str(GEN))

import os
import time
from concurrent import futures

import grpc
from generated import (
    report_pb2, report_pb2_grpc,
    user_pb2, user_pb2_grpc,
    order_pb2, order_pb2_grpc,
)

USERSVC_ADDR = os.getenv("USERSVC_ADDR", "localhost:50051")
ORDERSVC_ADDR = os.getenv("ORDERSVC_ADDR", "localhost:50052")


class ReportService(report_pb2_grpc.ReportServiceServicer):
    def __init__(self, user_stub, order_stub):
        self.user = user_stub
        self.order = order_stub

    def GetUserOrdersReport(self, request, context):
        try:
            u = self.user.GetUser(user_pb2.GetUserRequest(id=request.user_id), timeout=2)
        except grpc.RpcError as e:
            context.abort(e.code(), f"user lookup failed: {e.details()}")

        orders = self.order.ListOrders(order_pb2.ListOrdersRequest(user_id=u.id), timeout=3).orders
        total = sum(o.total for o in orders)

        return report_pb2.UserOrdersReportResponse(
            user_id=u.id,
            user_name=u.name,
            user_email=u.email,
            orders_count=len(orders),
            orders_total=total,
        )

    def GetTopUsersByOrders(self, request, context):
        users = self.user.ListUsers(user_pb2.ListUsersRequest(), timeout=3).users
        orders = self.order.ListOrders(order_pb2.ListOrdersRequest(), timeout=3).orders

        by_user = {u.id: {"name": u.name, "count": 0, "total": 0.0} for u in users}
        for o in orders:
            if o.user_id in by_user:
                by_user[o.user_id]["count"] += 1
                by_user[o.user_id]["total"] += o.total

        entries = sorted(
            (
                report_pb2.TopUsersByOrdersResponse.Entry(
                    user_id=uid,
                    user_name=data["name"],
                    orders_count=data["count"],
                    orders_total=data["total"],
                )
                for uid, data in by_user.items()
            ),
            key=lambda e: (e.orders_count, e.orders_total),
            reverse=True,
        )

        top_n = max(1, request.top_n or 5)
        return report_pb2.TopUsersByOrdersResponse(entries=entries[:top_n])


def _ready(addr: str):
    ch = grpc.insecure_channel(addr)
    grpc.channel_ready_future(ch).result(timeout=2)
    return ch


def serve():
    for _ in range(20):
        try:
            user_ch = _ready(USERSVC_ADDR)
            order_ch = _ready(ORDERSVC_ADDR)
            break
        except Exception:
            time.sleep(0.2)
    else:
        raise RuntimeError("Could not connect to dependent services")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    report_pb2_grpc.add_ReportServiceServicer_to_server(
        ReportService(
            user_stub=user_pb2_grpc.UserServiceStub(user_ch),
            order_stub=order_pb2_grpc.OrderServiceStub(order_ch),
        ),
        server,
    )
    server.add_insecure_port("[::]:50053")
    server.start()
    print(f"ReportService listening on :50053 (User:{USERSVC_ADDR} Order:{ORDERSVC_ADDR})")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
