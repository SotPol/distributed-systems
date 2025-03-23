import hazelcast
import time
from hazelcast import client


CONFIG = {
    "cluster_name": "dev",
    "cluster_members": [],
}


def task3():
    client = hazelcast.HazelcastClient(**CONFIG)
    try:
        distributed_map = client.get_map("distributed-map").blocking()
        for index in range(1, 1001):
            distributed_map.put(index, index)
            print(f"Inserted: {index}")
    finally:
        client.shutdown()


def task4():
    client = hazelcast.HazelcastClient(**CONFIG)
    key = "no_locks"
    distributed_map = client.get_map("distributed-map").blocking()


    if not distributed_map.contains_key(key):
        distributed_map.put(key, 0)


    start_time = time.time()
    for _ in range(10_000):
        value = distributed_map.get(key)
        distributed_map.put(key, value + 1)
    end_time = time.time()


    print(f"Final value (No Locks): {distributed_map.get(key)}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


    client.shutdown()


def task5():
    client = hazelcast.HazelcastClient(**CONFIG)
    key = "pessimistic_lock"
    distributed_map = client.get_map("distributed-map").blocking()


    if not distributed_map.contains_key(key):
        distributed_map.put(key, 0)


    start_time = time.time()
    for _ in range(10_000):
        distributed_map.lock(key)
        try:
            value = distributed_map.get(key)
            distributed_map.put(key, value + 1)
        finally:
            distributed_map.unlock(key)
    end_time = time.time()


    print(f"Final value (Pessimistic Locking): {distributed_map.get(key)}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


    client.shutdown()


def task6():
    client = hazelcast.HazelcastClient(**CONFIG)
    key = "optimistic_lock"
    distributed_map = client.get_map("distributed-map").blocking()


    if not distributed_map.contains_key(key):
        distributed_map.put(key, 0)


    start_time = time.time()
    for _ in range(10_000):
        while True:
            old_value = distributed_map.get(key)
            new_value = old_value + 1
            if distributed_map.replace_if_same(key, old_value, new_value):
                break
    end_time = time.time()


    print(f"Final value (Optimistic Locking): {distributed_map.get(key)}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


    client.shutdown()


def writer():
    client = hazelcast.HazelcastClient(**CONFIG)
    queue = client.get_queue("bounded-queue").blocking()
    
    try:
        for value in range(1, 101):
            queue.put(value)
            print(f"Додано в чергу: {value}")
            time.sleep(0.1)
    finally:
        client.shutdown()


def reader():
    client = hazelcast.HazelcastClient(**CONFIG)
    queue = client.get_queue("bounded-queue").blocking()
    
    try:
        while True:
            item = queue.take()
            print(f"Прочитано з черги: {item}")
    finally:
        client.shutdown()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Вкажіть 'writer', 'reader', або одну з task3-task6 для запуску відповідного клієнта.")
    elif sys.argv[1] == "writer":
        writer()
    elif sys.argv[1] == "reader":
        reader()
    elif sys.argv[1] == "task3":
        task3()
    elif sys.argv[1] == "task4":
        task4()
    elif sys.argv[1] == "task5":
        task5()
    elif sys.argv[1] == "task6":
        task6()
    else:
        print("Неправильний аргумент. Використовуйте 'writer', 'reader', 'task3', 'task4', 'task5' або 'task6'.")