int main(int argc, char** argv)
{
    using namespace std;
    Body body = parse(argv[1]);

    int total = 0;
    for (int i = 0; i < body.numbers.size(); i++)
    {
        total += body.numbers[i];
    }
    cout << total << endl;
    if (body.z)
    {
        cout << "T" << endl;
    }
    else
    {
        cout << "F" << endl;
    }
    for (int i = 0; i < body.str_array.size(); i++)
    {
        for (int j = 0; j < body.str_array[i].size(); j++)
        {
            cout << body.str_array[i][j] << endl;
        }
    }
    total = 0;
    for (int i = 0; i < body.int_array.size(); i++)
    {
        total += body.int_array[i];
    }
    cout << total << endl;
}
