import pytest
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Collection, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def _authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return _authenticate


@pytest.fixture
def create_collection(api_client):
    def _create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return _create_collection


@pytest.mark.django_db
class TestCreateCollection:

    def test_if_user_is_anonymous_returns_401(self, api_client, authenticate, create_collection):
        response = create_collection({'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client, authenticate, create_collection):
        authenticate()
        response = create_collection({'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, api_client, authenticate, create_collection):
        authenticate(is_staff=True)
        response = create_collection({'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, api_client, authenticate, create_collection):
        authenticate(is_staff=True)
        response = create_collection({'title': 'a'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:

    def test_if_collection_exists_return_200(self, api_client):
        collection = baker.make(Collection)
        # baker.make(Product, collection=collection, _quantity=10)
        response = api_client.get(f'/store/collections/{collection.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0,
        }

    def test_if_collection_does_not_exist_return_404(self, api_client):
        response = api_client.get('/store/collections/0/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
