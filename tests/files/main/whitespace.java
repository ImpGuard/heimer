public static void main(String[] args)
{
    Body body = parse(args[0]);

    for (Complex x : body.numbers)
    {
        System.out.println(x.a);
        System.out.println(x.b);
    }
}
