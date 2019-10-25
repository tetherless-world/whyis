class TestTableview():

    def test_get(self):
        graph = "temp"
        content = self.client.get("/table/" + graph)
        print(content)
