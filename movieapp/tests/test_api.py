from django.test import TestCase, Client
import json
from django.test import TestCase, Client

# initialize the APIClient app
client = Client()


# Create your tests here.
class TestMyAPI(TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000/"
        self.username = "user24"
        self.password = "admin"

    def test_register_user(self):
        """Test User registration API"""
        register_data = {"username": self.username, "password": self.password}
        response = client.post(self.base_url + "register/", data=register_data)
        self.assertEqual(response.status_code, 201)
        all_keys = response.json().keys()
        self.assertEqual("access" in all_keys, True)
        self.assertEqual("refresh" in all_keys, True)

    def test_false_register_user(self):
        """Test User registration API for already present user"""
        register_data = {"username": self.username, "password": self.password}
        response = client.post(self.base_url + "register/", data=register_data)
        register_data = {"username": self.username, "password": self.password}
        response = client.post(self.base_url + "register/", data=register_data)
        response_dict = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_dict["message"], "Username already exists")

    def test_post_collection(self):
        """Test POST request for creating new Collection"""
        self.register_user()
        headers = {
            "Authorization": "Bearer " + self.access,
            "content-type": "application/json",
        }
        response = self.post_a_collection(headers)
        self.assertEqual(response.status_code, 201)

    def test_get_all_collection(self):
        """Test GET API for fetching all Collections for a User alongwith top 3 favorite genres"""
        self.register_user()
        headers = {
            "Authorization": "Bearer " + self.access,
            "content-type": "application/json",
        }
        response = self.post_a_collection(headers)
        response = client.get(self.base_url + "collection/", headers=headers)
        all_keys = response.json().keys()
        self.assertEqual("is_success" in all_keys, True)
        self.assertEqual("data" in all_keys, True)
        self.assertEqual(response.status_code, 200)

    def test_get_single_collection(self):
        """Test GET API to fetch a single Collection using its uuid"""
        self.register_user()

        headers = {
            "Authorization": "Bearer " + self.access,
            "content-type": "application/json",
        }
        response = self.post_a_collection(headers)
        response_dict = json.loads(response.content)

        self.collection_uuid = response_dict.get("collection_uuid")
        response = client.get(
            self.base_url + "collection/" + self.collection_uuid + "/", headers=headers
        )
        all_keys = response.json().keys()
        self.assertEqual("title" in all_keys, True)
        self.assertEqual("description" in all_keys, True)
        self.assertEqual("movies" in all_keys, True)
        self.assertEqual(response.status_code, 200)

    def test_false_get_single_collection(self):
        """Test GET API to fetch a single Collection using its uuid"""
        self.register_user()

        headers = {
            "Authorization": "Bearer " + self.access,
            "content-type": "application/json",
        }
        response = self.post_a_collection(headers)
        response_dict = json.loads(response.content)

        self.collection_uuid = response_dict.get("collection_uuid")
        new_collection_uuid = self.collection_uuid[::-1]
        response = client.get(
            self.base_url + "collection/" + new_collection_uuid + "/", headers=headers
        )
        response_dict = json.loads(response.content)
        self.assertEqual(
            response_dict["message"],
            f"Collection does not exist for UUID {new_collection_uuid}",
        )
        self.assertEqual(response.status_code, 404)

    def test_put_collection(self):
        """Test PUT API to update a given Collection"""
        self.register_user()

        headers = {
            "Authorization": "Bearer " + self.access,
            "content-type": "application/json",
        }
        response = self.post_a_collection(headers)
        response_dict = json.loads(response.content)
        self.collection_uuid = response_dict.get("collection_uuid")

        put_data = {"title": "Collection title new", "description": "New description of Collection"}
        put_url = self.base_url + "collection/" + self.collection_uuid + "/"
        response = client.put(
            put_url,
            json.dumps(put_data),
            "application/json",
            headers=headers,
        )
        response_dict = json.loads(response.content)
        self.assertEqual(response_dict.get("title"), put_data["title"])
        self.assertEqual(response_dict.get("description"), put_data["description"])
        self.assertEqual(response.status_code, 200)

    def test_delete_collection(self):
        """Test DELETE API for deleting a Collection"""
        self.register_user()

        headers = {
            "Authorization": "Bearer " + self.access,
            "content-type": "application/json",
        }
        response = self.post_a_collection(headers)
        response_dict = json.loads(response.content)
        self.collection_uuid = response_dict.get("collection_uuid")
        response = client.delete(
            self.base_url + "collection/" + self.collection_uuid + "/",
            headers=headers,
        )
        self.assertEqual(response.status_code, 204)

    def test_request_count(self):
        """Test GET request for request_count; the number of requests that the server has received"""
        response = client.get(self.base_url + "request-count/")
        self.assertEqual(response.status_code, 200)

    def test_reset_count(self):
        """Test POST request to reset the request_count value to 0"""
        response = client.post(self.base_url + "request-count/reset/")
        self.assertEqual(response.status_code, 205)

    # helper functions

    def register_user(self):
        register_data = {"username": self.username, "password": self.password}
        response = client.post(self.base_url + "register/", data=register_data)
        response_dict = json.loads(response.content)
        self.access = response_dict.get("access")

    def post_a_collection(self, headers):
        post_data = {
            "title": "Collection title",
            "description": "Description of Collection",
            "movies": [
                {
                    "title": "L'Homme orchestre",
                    "description": "A band-leader has arranged seven chairs for the members of his band. When he sits down in the first chair, a cymbal player appears in the same chair, then rises and sits in the next chair. As the cymbal player sits down, a drummer appears in the second chair, and then likewise moves on to the third chair. In this way, an entire band is soon formed, and is then ready to perform.",
                    "genres": "Fantasy,Action,Thriller",
                    "uuid": "cc75c16e-c72d-444f-93db-1b8764555be0",
                }
            ],
        }
        response = client.post(
            self.base_url + "collection/",
            json.dumps(post_data),
            "application/json",
            headers=headers,
        )
        return response
