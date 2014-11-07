if __name__ == "__main__":
    body = run(sys.argv)
    print sum(body.a.numbers) * sum(body.b.numbers) * sum(body.c.numbers) * sum(body.d.numbers)
