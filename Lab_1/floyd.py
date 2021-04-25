INF = float("INF")


class Floyd:

    def __init__(self, weight_matrix):
        self.v = len(weight_matrix)
        self.weight_matrix = weight_matrix
        self.dist = list(map(lambda i: list(map(lambda j: j, i)), weight_matrix))
        self.path = [[0 for j in range(self.v)] for i in range(self.v)]
        self.path_out = []

    def floyd_warshall(self):
        for k in range(self.v):
            for i in range(self.v):
                for j in range(self.v):
                    if self.dist[i][j] > self.dist[i][k] + self.dist[k][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.path[i][j] = k

    def print_solution(self):
        print(
            "Following matrix shows the shortest distances between every pair of vertices")
        for i in range(self.v):
            for j in range(self.v):
                if (self.dist[i][j] == 0):
                    print("INF ", end='')
                else:
                    print(self.dist[i][j], '', end='')
                if j == self.v - 1:
                    print()

    def path_p(self, i, j):
        k = self.path[i][j]
        if k == 0:
            return
        self.path_p(i, k)
        self.path_out.append('X' + str(k + 1))
        self.path_p(k, j)

    def get_path(self, i, j):
        self.path_p(i, j)
        path = 'X' + str(i + 1) + '->'
        for node in self.path_out:
            path += node + '->'
        path += 'X' + str(j + 1)
        return path

    def get_node_list(self, i, j) -> list:
        # self.path_p(i, j)
        self.path_out.insert(0, 'X' + str(i + 1))
        self.path_out.append('X' + str(j + 1))
        return self.path_out
