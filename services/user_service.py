import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
if str(GEN) not in sys.path:
    sys.path.insert(0, str(GEN))

import grpc
from concurrent import futures
import uuid
from google.protobuf import empty_pb2


from generated import user_pb2, user_pb2_grpc


class InMemoryUserRepo:
    def __init__(self):
        self.users = {}


    def create(self, name: str, email: str):
        uid = str(uuid.uuid4())
        user = user_pb2.User(id=uid, name=name, email=email)
        self.users[uid] = user
        return user


    def get(self, uid: str):
        return self.users.get(uid)


    def list(self):
        return list(self.users.values())


    def update(self, uid: str, name: str, email: str):
        user = self.users.get(uid)
        if not user:
            return None
        user.name = name or user.name
        user.email = email or user.email
        return user


    def delete(self, uid: str):
        self.users.pop(uid, None)


class UserService(user_pb2_grpc.UserServiceServicer):
    def __init__(self, repo: InMemoryUserRepo):
        self.repo = repo


    def CreateUser(self, request, context):
        if not request.name or not request.email:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "name and email are required")
        return self.repo.create(request.name, request.email)

    def GetUser(self, request, context):
        user = self.repo.get(request.id)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, "user not found")
        return user


    def ListUsers(self, request, context):
        return user_pb2.ListUsersResponse(users=self.repo.list())


    def UpdateUser(self, request, context):
        user = self.repo.update(request.id, request.name, request.email)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, "user not found")
        return user


    def DeleteUser(self, request, context):
        self.repo.delete(request.id)
        return empty_pb2.Empty()




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(InMemoryUserRepo()), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("UserService listening on :50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()