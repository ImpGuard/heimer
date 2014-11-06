if __name__ == "__main__":
    body = run(sys.argv)
    for graph in body.graphs:
        print graph.name
        for adjacency in graph.adjacencies:
            total = 0
            total += adjacency.vertex
            for neighbor in adjacency.neighbors:
                total += neighbor
            print total
