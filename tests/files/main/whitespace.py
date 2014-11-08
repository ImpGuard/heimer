if __name__ == "__main__":
    body = parse(sys.argv[1])
    for n in body.numbers:
        print n.a
        print n.b
