import heapq


class TopKHeap:
    def __init__(self, k):
        self.k = k
        self.data = []
        self.total_len = 0

    def push(self, element):
        element = (element[0], self.total_len, element[1])

        if len(self.data) < self.k:
            # add data_len to preserve stability
            # and prevent comparing the second object
            # which is probably incomparable
            heapq.heappush(self.data, element)
        else:
            smallest = self.data[0]
            if element > smallest:
                heapq.heapreplace(self.data, element)

        self.total_len += 1

    def top_k(self):
        data_len = len(self.data)
        # return priority to sort
        return [element for element in reversed([heapq.heappop(self.data) for _ in range(data_len)])]
