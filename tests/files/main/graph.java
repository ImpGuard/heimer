public static void main(String[] args)
{
    Body body = run(args);

    for (Graph graph : body.graphs)
    {
        System.out.println(graph.name);
        for (Adjacency adjacency : graph.adjacencies)
        {
            int total = 0;
            total += adjacency.vertex;
            for (int neighbor : adjacency.neighbors)
            {
                total += neighbor;
            }
            System.out.println(total);
        }
    }
}
