public static void main(String[] args)
{
    Body body = run(args);

    for (Complex x : body.numbers)
    {
        System.out.println(x.a);
        System.out.println(x.b);
    }
}
