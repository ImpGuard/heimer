int main(int argc, char** argv)
{
    using namespace std;
    Body body;
    run(argc, argv, body);

    int result = 1;
    int total = 0;
    for (int i = 0; i < body.a.numbers.size(); i++)
    {
        total += body.a.numbers[i];
    }
    result *= total;
    total = 0;
    for (int i = 0; i < body.b.numbers.size(); i++)
    {
        total += body.b.numbers[i];
    }
    result *= total;
    total = 0;
    for (int i = 0; i < body.c.numbers.size(); i++)
    {
        total += body.c.numbers[i];
    }
    result *= total;
    total = 0;
    for (int i = 0; i < body.d.numbers.size(); i++)
    {
        total += body.d.numbers[i];
    }
    result *= total;

    cout << result << endl;
}
