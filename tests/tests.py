def test_fantasy():
    with open("./tests/fantasy.txt", "r", encoding="utf-8") as fantasy:
        check_value = len(fantasy.read())
        assert check_value == 27156, f"Should be 27156 but is {check_value}"


def test_adnd():
    with open("./tests/adnd.txt", "r", encoding="utf-8") as adnd:
        check_value = len(adnd.read())
        assert check_value == 83305, f"Should be 83305 but is {check_value}"


def test_4e():
    with open("./tests/4e.txt", "r", encoding="utf-8") as fourth:
        check_value = len(fourth.read())
        assert check_value == 91205, f"Should be 91205 but is {check_value}"


def test_5e():
    with open("./tests/5e.txt", "r", encoding="utf-8") as fifth:
        check_value = len(fifth.read())
        assert check_value == 42706, f"Should be 42706 but is {check_value}"


if __name__ == "__main__":
    test_fantasy()
    test_adnd()
    test_4e()
    # test_5e()
    print("Everything passed")