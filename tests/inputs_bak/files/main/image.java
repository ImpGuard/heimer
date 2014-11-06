public static void main(String[] args) {
    Body image = run(args);

    System.out.print(image.header.name + " " + image.header.size.x + " " + image.header.size.y + "\n");
    for (ArrayList<Integer> line : image.data) {
        for (int number : line) {
            System.out.print(number);
        }
        System.out.println();
    }
}
