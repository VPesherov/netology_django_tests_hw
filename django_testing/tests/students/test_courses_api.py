import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student

API_URL = '/api/v1/courses/'


@pytest.fixture()
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture()
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_get_first_course(api_client, course_factory):
    # Arrange - подготовка данных
    # client = APIClient()
    courses = course_factory(_quantity=5)
    # print(courses[0].id)
    # Act - тестируемый функционал
    response = api_client.get(f'{API_URL}{courses[0].id}/')
    # Assert - проверка
    data = response.json()
    # print(data['id'])
    assert courses[0].id == data['id']


@pytest.mark.django_db
def test_get_course_list(api_client, course_factory):
    courses = course_factory(_quantity=10)
    response = api_client.get(f'{API_URL}')
    data = response.json()
    for i, d in enumerate(data):
        assert d['id'] == courses[i].id
    # assert courses == data


@pytest.mark.django_db
def test_get_course_with_filter(api_client, course_factory):
    courses = course_factory(_quantity=10)
    response = api_client.get(f'{API_URL}?id={courses[0].id}')
    data = response.json()
    # print(data)
    assert data[0]['id'] == courses[0].id

    response = api_client.get(f'{API_URL}?name={courses[0].name}')
    data = response.json()
    assert data[0]['name'] == courses[0].name


@pytest.mark.django_db
def test_create_course(api_client):
    count = Course.objects.count()
    api_client.post(f"{API_URL}", data={"name": 'test course', "text": []}, format="json")
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    courses = course_factory(_quantity=10)
    old_name = courses[0].name
    new_name = 'new name123'
    api_client.put(f'{API_URL}{courses[0].id}/', data={"name": new_name}, format='json')

    response = api_client.get(f'{API_URL}{courses[0].id}/')
    data = response.json()
    assert old_name != data['name']
    assert data['name'] == new_name


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    courses = course_factory(_quantity=10)
    count = Course.objects.count()
    response = api_client.get(f'{API_URL}{courses[0].id}/')

    api_client.delete(f'{API_URL}{courses[0].id}/')
    response_after_delete = api_client.get(f'{API_URL}{courses[0].id}/')
    assert Course.objects.count() == count - 1
    assert response.status_code == 200
    assert response_after_delete.status_code == 404
