from threading import Lock
from concurrent.futures import ThreadPoolExecutor


class SharedResource:
    def __init__(self, value=0):
        self.value = value


def resource_state_change(arg: int, lock: Lock, resource: SharedResource):
    with lock:
        resource.value += arg


def main():
    lock = Lock()
    shared_resource = SharedResource()
    with ThreadPoolExecutor(max_workers=5) as executor:
        for _ in range(5):
            executor.submit(resource_state_change, 1000000, lock, shared_resource)
    print("----------------------", shared_resource.value)


main()
