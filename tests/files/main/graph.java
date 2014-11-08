public static void main(String[] args)
{
    Body body = parse(args[0]);

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
