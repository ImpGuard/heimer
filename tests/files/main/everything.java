public static void main(String[] args) {
    Body body = run(args);

    int sum = 0;
    for (Integer i : body.numbers)
        sum += i;
    System.out.println(sum);
    if (body.z)
        System.out.println("T");
    else
        System.out.println("F");
    String res = "";
    for (ArrayList<String> lines : body.str_array) {
        for (String s : lines)
            res += s + " ";
        res = res.substring(0, res.length() - 1) + ", ";
    }
    System.out.println(res.substring(0, res.length() - 2));
    sum = 0;
    for (Integer i : body.int_array)
        sum += i;
    System.out.println(sum);
}
