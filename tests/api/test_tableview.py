import json
from whyis.test.api_test_case import ApiTestCase

testdata = [
    {"id":1,"name":"Billy Bob","age":"12","col":"red","dob":""},
    {"id":2,"name":"Mary May","age":"1","col":"blue","dob":"14/05/1982"},
    {"id":3,"name":"Christine Lobowski","age":"42","height":0,"col":"green","dob":"22/05/1982","cheese":"true"},
    {"id":4,"name":"Brendon Philips","age":"125","gender":"male","height":1,"col":"orange","dob":"01/08/1980"},
    {"id":5,"name":"Margret Marmajuke","age":"16","gender":"female","height":5,"col":"yellow","dob":"31/01/1999"},
    {"id":6,"name":"Billy Bob","age":"12","gender":"male","height":1,"col":"red","dob":"","cheese":1},
    {"id":7,"name":"Mary May","age":"1","gender":"female","height":2,"col":"blue","dob":"14/05/1982","cheese":True},
    {"id":8,"name":"Christine Lobowski","age":"42","height":0,"col":"green","dob":"22/05/1982","cheese":"true"},
    {"id":9,"name":"Brendon Philips","age":"125","gender":"male","height":1,"col":"orange","dob":"01/08/1980"},
    {"id":10,"name":"Margret Marmajuke","age":"16","gender":"female","height":5,"col":"yellow","dob":"31/01/1999"}
]
class TestTableview(ApiTestCase):

    def test_get(self):
        #print('\nTEST: Getting test_table')
        tableid = "test_table"
        response = self.client.get("/table/" + tableid, follow_redirects=True)
        #print(response)
        self.assertEqual(response.json, testdata)

    def test_post(self):
        #print('\nSTART TEST POST')
        data = json.dumps(testdata)
        tableid = "test_table"
        response = self.client.post("/table/" + tableid, data=data, follow_redirects=True)
        #print(response)
        self.assertEqual(response.status_code, 204)

    def test_delete(self):
        #print('\nTEST: Deleting delete_table')
        tableid = "delete_table"
        response = self.client.delete("/table/" + tableid)
        #print("Response:", response)
        self.assertEqual(response.status_code, 204)
        get_response = self.client.get("/table/" + tableid, follow_redirects=True)
        #print(get_response)
        self.assertEqual(get_response.status_code, 404)

    def test_put(self):
        #print('\nSTART TEST PUT')
        tableid = "test_table"
        response = self.client.put("/table/" + tableid)
        #print(response)
        self.assertEqual(response.status_code, 201)
