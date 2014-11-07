if __name__ == "__main__":
    body = run(sys.argv)
    print sum(body.numbers)
    print ("T" if body.z else "F")
    for s_list in body.str_array:
        for s in s_list:
            print s
    print sum(body.int_array)
