public static void main(String[] args)
{
    Body body = parse(args[0]);

    int total = 0;
    for (int n : body.numbers)
    {
        total += n;
    }
    System.out.println(total);
    if (body.z)
    {
        System.out.println("T");
    }
    else
    {
        System.out.println("F");
    }
    for (ArrayList<String> s_list : body.str_array)
    {
        for (String s : s_list)
        {
            System.out.println(s);
        }
    }
    total = 0;
    for (int n : body.int_array)
    {
        total += n;
    }
    System.out.println(total);
}
