TEST_KEY = "Bearer sk_test_02983bb23375062385e2086654693ce77caf4a0c"
JSON_CONTENT = "application/json"

def get_headers():
    return {
        "Authorization": TEST_KEY,
        "Content-Type": JSON_CONTENT
    }
