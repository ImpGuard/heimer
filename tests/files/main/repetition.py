if __name__ == "__main__":
    body = parse(sys.argv[1])
    print sum(body.a.numbers) * sum(body.b.numbers) * sum(body.c.numbers) * sum(body.d.numbers)
