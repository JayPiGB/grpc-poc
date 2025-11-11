import os
import grpc
from generated import (
    user_pb2, user_pb2_grpc,
    order_pb2, order_pb2_grpc,
    report_pb2, report_pb2_grpc,
)

USERSVC = os.getenv("USERSVC_ADDR", "localhost:50051")
ORDERSVC = os.getenv("ORDERSVC_ADDR", "localhost:50052")
REPORTSVC = os.getenv("REPORTSVC_ADDR", "localhost:50053")


def main():
    user_ch = grpc.insecure_channel(USERSVC)
    order_ch = grpc.insecure_channel(ORDERSVC)
    report_ch = grpc.insecure_channel(REPORTSVC)

    user = user_pb2_grpc.UserServiceStub(user_ch)
    order = order_pb2_grpc.OrderServiceStub(order_ch)
    report = report_pb2_grpc.ReportServiceStub(report_ch)

    u1 = user.CreateUser(user_pb2.CreateUserRequest(name="Alice", email="alice@example.com"))
    u2 = user.CreateUser(user_pb2.CreateUserRequest(name="Bob", email="bob@example.com"))
    print("Users created:", [u1, u2])
    print("---------------------------")

    o1 = order.CreateOrder(order_pb2.CreateOrderRequest(user_id=u1.id, items=["book", "pen"], total=50.0))
    o2 = order.CreateOrder(order_pb2.CreateOrderRequest(user_id=u1.id, items=["notebook"], total=25.0))
    o3 = order.CreateOrder(order_pb2.CreateOrderRequest(user_id=u2.id, items=["mouse"], total=80.0))
    print("Orders created:")
    print(o1)
    print(o2)
    print(o3)
    print("---------------------------")

    report_alice = report.GetUserOrdersReport(report_pb2.UserOrdersReportRequest(user_id=u1.id))
    print("Report Alice:", report_alice)

    report_bob = report.GetUserOrdersReport(report_pb2.UserOrdersReportRequest(user_id=u2.id))
    print("Report Bob:", report_bob)

if __name__ == "__main__":
    main()
