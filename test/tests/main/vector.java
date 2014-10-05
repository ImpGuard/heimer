public static float calculateMagnitude(Vector v) {
    float x = v.end.x - v.start.x;
    float y = v.end.y - v.start.y;
    float z = v.end.z - v.start.z;

    return (float) Math.sqrt(x * x + y * y + z * z);
}

public static void main(String[] args) {
    Body stuff = run(args);

    for (Vector v : stuff.vectors) {
        System.out.format("%.1f\n", calculateMagnitude(v));
    }
    System.out.println(stuff.p.x + stuff.p.y + stuff.p.z);
}
