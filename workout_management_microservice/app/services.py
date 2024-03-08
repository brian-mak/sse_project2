from .models import db, SavedList, SavedListWorkout
from sqlalchemy.exc import SQLAlchemyError

def create_saved_list_service(user_id, list_name):
    """
    Service to create a new saved list for a user.
    """
    new_saved_list = SavedList(UserID=user_id, Name=list_name)
    db.session.add(new_saved_list)
    try:
        db.session.commit()
        return {"success": True, "message": "Saved list created successfully.", "list_id": new_saved_list.ListID}
    except SQLAlchemyError as e:
        db.session.rollback()
        # Log the exception e here
        return {"success": False, "message": "Failed to create saved list due to a database error."}
    
def delete_saved_list_service(list_id):
    """
    Service to delete a saved list and all related workouts.
    """
    try:
        # Attempt to delete all related workouts first
        SavedListWorkout.query.filter_by(ListID=list_id).delete()
        # Then delete the saved list itself
        saved_list_to_delete = SavedList.query.filter_by(ListID=list_id).first()
        if saved_list_to_delete:
            db.session.delete(saved_list_to_delete)
            db.session.commit()
            return {"success": True, "message": "Saved list and related workouts deleted successfully."}
        else:
            return {"success": False, "message": "Saved list not found."}
    except SQLAlchemyError as e:
        db.session.rollback()
        # Log the exception e here
        return {"success": False, "message": f"Database error, couldn't delete saved list and workouts: {e}"}

def get_saved_lists_service(user_id):
    """
    Service to get all saved lists for a user.
    """
    try:
        saved_lists = SavedList.query.filter_by(UserID=user_id).all()
        return [{"list_id": sl.ListID, "name": sl.Name} for sl in saved_lists]
    except SQLAlchemyError as e:
        # Log the exception e here
        return {"success": False, "message": "Failed to retrieve saved lists due to a database error."}

def get_workouts_for_saved_list_service(list_id):
    """
    Service to get all workouts for a specific saved list.
    """
    try:
        workouts = SavedListWorkout.query.filter_by(ListID=list_id).all()
        print(workouts)
        return [
            {
                "workout_id": w.WorkoutID,
                "workout_name": w.WorkoutName,
                "equipment": w.Equipment,
                "target_muscle_group": w.TargetMuscleGroup,
                "secondary_muscles": w.SecondaryMuscles,
            }
            for w in workouts
        ]
    except SQLAlchemyError as e:
        # Log the exception e here
        return {"success": False, "message": "Failed to retrieve workouts for saved list due to a database error."}

def fetch_workouts_service(target_muscle_groups, available_equipment):
    """
    Fetch exercises filtered by target muscle groups and available equipment.
    """
    try:
        workouts = SavedListWorkout.query.filter(
            SavedListWorkout.TargetMuscleGroup.in_(target_muscle_groups),
            SavedListWorkout.Equipment.in_(available_equipment)
        ).all()
        return workouts
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        return []

def add_workout_to_saved_list_service(list_id, workout_id, workout_name, equipment, target_muscle_group, secondary_muscles):
    """
    Add a workout to a saved list.
    """
    try:
        new_workout = SavedListWorkout(
            ListID=list_id,
            WorkoutID=workout_id,
            WorkoutName=workout_name,
            Equipment=equipment,
            TargetMuscleGroup=target_muscle_group,
            SecondaryMuscles=secondary_muscles
        )
        db.session.add(new_workout)
        db.session.commit()
        return {"success": True, "message": "Workout added successfully to the saved list."}
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Failed to add workout to saved list: {e}")
        return {"success": False, "message": "Database error, couldn't add workout."}

def remove_workout_from_saved_list_service(list_id, workout_id):
    """
    Remove a workout from a saved list.
    """
    try:
        workout_to_remove = SavedListWorkout.query.filter_by(ListID=list_id, WorkoutID=workout_id).first()
        if workout_to_remove:
            db.session.delete(workout_to_remove)
            db.session.commit()
            return {"success": True, "message": "Workout removed from saved list successfully."}
        else:
            return {"success": False, "message": "Workout not found in the saved list."}
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Failed to remove workout from saved list: {e}")
        return {"success": False, "message": "Database error, couldn't remove workout."}
