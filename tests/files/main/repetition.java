public static void main(String[] args)
{
    Body body = parse(args[0]);

    int result = 1;
    int total = 0;
    for (int i : body.a.numbers)
    {
        total += i;
    }
    result *= total;
    total = 0;
    for (int i : body.b.numbers)
    {
        total += i;
    }
    result *= total;
    total = 0;
    for (int i : body.c.numbers)
    {
        total += i;
    }
    result *= total;
    total = 0;
    for (int i : body.d.numbers)
    {
        total += i;
    }
    result *= total;

    System.out.println(result);
}
