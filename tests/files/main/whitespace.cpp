int main(int argc, char** argv) {
    using namespace std;
    Body body;
    run(argc, argv, body);

    for (int i = 0; i < body.numbers.size(); i++) {
        cout << body.numbers[i].a << endl
             << body.numbers[i].b << endl;
    }
}
