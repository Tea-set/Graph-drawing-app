# Python Program for Floyd Warshall Algorithm

# Number of vertices in the graph


# Define infinity as the large
# enough value. This value will be
# used for vertices not connected to each other
INF = float("INF")


# Solves all pair shortest path
# via Floyd Warshall Algorithm

def floydWarshall(graph):
    v = len(graph)
    """ dist[][] will be the output
       matrix that will finally
        have the shortest distances
        between every pair of vertices """
    """ initializing the solution matrix
    same as input graph matrix
    OR we can say that the initial
    values of shortest distances
    are based on shortest paths considering no
    intermediate vertices """

    dist = list(map(lambda i: list(map(lambda j: j, i)), graph))

    """ Add all vertices one by one
    to the set of intermediate
     vertices.
     ---> Before start of an iteration,
     we have shortest distances
     between all pairs of vertices
     such that the shortest
     distances consider only the
     vertices in the set
    {0, 1, 2, .. k-1} as intermediate vertices.
      ----> After the end of a
      iteration, vertex no. k is
     added to the set of intermediate
     vertices and the
    set becomes {0, 1, 2, .. k}
    """
    for k in range(v):

        # pick all vertices as source one by one
        for i in range(v):

            # Pick all vertices as destination for the
            # above picked source
            for j in range(v):
                # If vertex k is on the shortest path from
                # i to j, then update the value of dist[i][j]
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    printSolution(dist, v)


# A utility function to print the solution
def printSolution(dist, v):
    print(
        "Following matrix shows the shortest distances between every pair of vertices")
    for i in range(v):
        for j in range(v):
            if (dist[i][j] == 0):
                print("INF ", end='')
            else:
                print(dist[i][j], '', end='')
            if j == v - 1:
                print()


# Driver program to test the above program
# Let us create the following weighted graph

graph = [[INF, 1, INF, INF, INF],
         [INF, INF, 10, INF, 2],
         [5, INF, INF, 6, INF],
         [INF, 8, INF, INF, INF],
         [7, INF, INF, 7, INF]
         ]
# Print the solution
floydWarshall(graph)
# This code is contributed by Mythri J L
