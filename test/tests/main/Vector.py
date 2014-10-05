if __name__ == "__main__":
    body = run(sys.argv)
    import math
    def magn(vector):
        x = float(vector.end.x - vector.start.x)
        y = float(vector.end.y - vector.start.y)
        z = float(vector.end.z - vector.start.z)
        return math.sqrt(x * x + y * y + z * z)
    for v in body.vectors:
        print magn(v)
    print (body.p.x + body.p.y + body.p.z)