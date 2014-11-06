int main(int argc, char** argv)
{
    using namespace std;
    Body body;
    run(argc, argv, body);

    for (int i = 0; i < body.graphs.size(); i++)
    {
        Graph &graph = body.graphs[i];
        cout << graph.name << endl;
        int total = 0;
        for (int j = 0; j < graph.adjacencies.size(); j++)
        {
            Adjacency &adjacency = graph.adjacencies[j];
            total += adjacency.vertex;
            for (int k = 0; k < adjacency.neighbors.size(); k++)
            {
                total += adjacency.neighbors[k];
            }
        }
        cout << total << endl;
    }
}
