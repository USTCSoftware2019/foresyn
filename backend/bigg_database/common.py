import heapq


class TopKHeap:
    def __init__(self, k):
        self.k = k
        self.data = []

    def push(self, element):
        if len(self.data) < self.k:
            heapq.heappop(self.data, element)
        else:
            smallest = self.data[0]
            if element > smallest:
                heapq.heapreplace(self.data, element)

    def top_k(self):
        data_len = len(self.data)
        return [element for element in reversed([heapq.heappop(self.data) for _ in range(data_len)])]
