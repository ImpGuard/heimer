if __name__ == "__main__":
    body = run(sys.argv)
    print body.header.name, body.header.size.x, body.header.size.y
    for line in body.data:
        s = ""
        for n in line:
            s += str(n)
        print s