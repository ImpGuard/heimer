if __name__ == "__main__":
    body = run(sys.argv)
    print ( sum(body.numbers) if body.numbers else 0 )
    print 'T' if body.z else 'F'
    print ", ".join([" ".join(body.str_array[0]), " ".join(body.str_array[1]), " ".join(body.str_array[2])])
    print sum(body.int_array)