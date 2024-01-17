import time
from multiprocessing import Pool, cpu_count

def factorize_number(n):
    factors = []
    for i in range(1, n + 1):
        if n % i == 0:
            factors.append(i)
    return factors

def factorize_sync(*numbers):
    results = []
    for number in numbers:
        factors = factorize_number(number)
        results.append(factors)
    return results

def factorize_parallel(*numbers):
    with Pool(cpu_count()) as pool:
        results = pool.map(factorize_number, numbers)
    return results

# Testy
def test_factorize():
    a, b, c, d = factorize_sync(128, 255, 99999, 10651060)
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

    return a, b, c, d

    start_time = time.time()
    factorize_sync(128, 255, 99999, 10651060)
    sync_execution_time = time.time() - start_time
    print(f"Synchronous execution time: {sync_execution_time} seconds")

    start_time = time.time()
    factorize_parallel(128, 255, 99999, 10651060)
    parallel_execution_time = time.time() - start_time
    print(f"Parallel execution time: {parallel_execution_time} seconds")

if __name__ == "__main__":
    start_time = time.time()
    result = factorize_sync(128, 255, 99999, 10651060)
    sync_execution_time = time.time() - start_time
    print(f"Synchronous execution time: {sync_execution_time} seconds")
    print("Result: ", result)
    start_time = time.time()
    result_2 = factorize_parallel(128, 255, 99999, 10651060)
    parallel_execution_time = time.time() - start_time
    print(f"Parallel execution time: {parallel_execution_time} seconds")
    print(f"Result: ", result_2)
#results = test_factorize()
    #print("Results:", results)

