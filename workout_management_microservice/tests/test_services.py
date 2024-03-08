import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from app.services import (
    create_saved_list_service,
    delete_saved_list_service,
    get_saved_lists_service, 
    get_workouts_for_saved_list_service, 
    fetch_workouts_service, 
    add_workout_to_saved_list_service, 
    remove_workout_from_saved_list_service
)

def test_create_saved_list_service():
    with patch('your_application.services.db.session.add'), \
         patch('your_application.services.db.session.commit'):
        result = create_saved_list_service(1, 'My List')
        assert result['success'] is True

def test_delete_saved_list_service():
    with patch('your_application.services.SavedList.query') as mock_query, \
         patch('your_application.services.db.session.commit'):
        mock_query.filter_by.return_value.first.return_value = MagicMock()
        result = delete_saved_list_service(1)
        assert result['success'] is True

def test_get_saved_lists_service():
    with patch('your_application.services.SavedList.query') as mock_query:
        mock_query.filter_by.return_value.all.return_value = []
        result = get_saved_lists_service(1)
        assert isinstance(result, list)

def test_get_workouts_for_saved_list_service():
    with patch('your_application.services.SavedListWorkout.query') as mock_query:
        mock_query.filter_by.return_value.all.return_value = []
        result = get_workouts_for_saved_list_service(1)
        assert isinstance(result, list)

def test_fetch_workouts_service():
    with patch('your_application.services.SavedListWorkout.query') as mock_query:
        mock_query.filter.return_value.all.return_value = []
        result = fetch_workouts_service(['arms'], ['dumbbell'])
        assert isinstance(result, list)

def test_add_workout_to_saved_list_service():
    with patch('your_application.services.db.session.add'), \
         patch('your_application.services.db.session.commit'):
        result = add_workout_to_saved_list_service(1, 1, 'Push Up', 'None', 'Chest', '')
        assert result['success'] is True

def test_remove_workout_from_saved_list_service():
    with patch('your_application.services.SavedListWorkout.query') as mock_query, \
         patch('your_application.services.db.session.commit'):
        mock_query.filter_by.return_value.first.return_value = MagicMock()
        result = remove_workout_from_saved_list_service(1, 1)
        assert result['success'] is True