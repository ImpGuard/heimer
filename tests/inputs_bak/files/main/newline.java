public static void main(String[] args) {
    Body body = run(args);

    for (ImaginaryNumber number : body.numbers) {
        System.out.println(number.real + " + " + number.imaginary + "i");
    }
    System.out.println();
    System.out.println(body.extra.real + " + " + body.extra.imaginary + "i");
}
