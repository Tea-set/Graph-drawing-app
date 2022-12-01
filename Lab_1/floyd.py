INF = float("INF")


class Floyd:

    def __init__(self, weight_matrix):
        self.v = len(weight_matrix)
        self.weight_matrix = weight_matrix
        self.dist = list(map(lambda i: list(map(lambda j: j, i)), weight_matrix))
        self.path = [[0 for j in range(self.v)] for i in range(self.v)]
        self.path_out = []

    def floyd_warshall(self):
        # Пробегает весю матрицу, находит кротчайшие пути, строит матрицу для нахождения этих путей
        for k in range(self.v):
            for i in range(self.v):
                for j in range(self.v):
                    if self.dist[i][j] > self.dist[i][k] + self.dist[k][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.path[i][j] = k

    def print_solution(self):
        # выводит матрицу кротчайших путей
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
        # рекурсивно обходит матрицу для поиска путей
        # выводит последоваетльность вершин
        k = self.path[i][j]
        if k == 0:
            return
        self.path_p(i, k)
        self.path_out.append('X' + str(k + 1))
        self.path_p(k, j)

    def get_path(self, i, j):
        # добовляет к предыдушему методу начальную и конечную вершины
        self.path_p(i, j)
        path = 'X' + str(i + 1) + '->'
        for node in self.path_out:
            path += node + '->'
        path += 'X' + str(j + 1)
        return path

    def get_node_list(self, i, j) -> list:
        # модифицирует список вершин, работате с листом
        # self.path_p(i, j)
        self.path_out.insert(0, 'X' + str(i + 1))
        self.path_out.append('X' + str(j + 1))
        return self.path_out


if __name__ == '__main__':
    graph = [[INF, INF, 3, INF],
             [2, INF, INF, INF],
             [INF, 7, INF, 1],
             [6, INF, INF, INF]]

    fl = Floyd(graph)
    fl.floyd_warshall()
    fl.print_solution()
    print(fl.path)
    print(fl.get_path(2,0))
    # print(fl.get_node_list(3,1))