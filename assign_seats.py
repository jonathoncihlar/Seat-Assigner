"""
Creates a seating assignments based on student requests. The algorithm works by randomly selecting a 
student and attempting to give them a preferred seat in ranked order. If no seat can be assigned, 
Inputs:
    Available seats file - A text file listing each available seat name, one per line
    Student Request File - A comma-separated text file. The student's name is first followed by a ranked 
        listing of their preferred seats. Students who have seating accommodations can be

Outputs:
    Seating chart where each row is a seat assignment: seat name, student

J. Cihlar - December 2025
"""

import sys
import random
import logging

# logger is set up as a module level variable
logger = logging.getLogger(__name__)

def load_student_requests(file_name: str, available_seats: set[str]) -> dict[str,list[str]] | None:
    """
    Loads student requests from file. Validates against the available seats. It only retains the first instance
    of a request and only if the seat appears in the list of available seats.
    
    Args:
        file_name (str): The filename of the student requests file.
        available_seats set(str): A set of strings representing the available seats
    
    Returns:
        dict: A dictionary where the keys are the student names. The values are a list of ranked seat preferences.
    """
    student_requests: dict[str, list[str]] = {}
    try:
        with open(file_name, "r") as file:
            for i, request in enumerate(file):
                pieces = [p.strip() for p in request.split(",")]
                # skip blank student names
                if pieces[0] == "":
                    logger.warning("No student name on line %d", i+1)
                    continue
                student = pieces[0] 
                seen: set[str] = set()
                seats: list[str] = []
                for seat in pieces[1:]:
                    # check that seat is not duplicate and a valid seat
                    if seat not in seen and seat in available_seats:
                        seats.append(seat)
                        seen.add(seat)
                if student not in student_requests:
                    student_requests[student] = seats
                else:
                    logger.warning("Duplicate student %s on line %d", student, i+1)
        return student_requests
    except FileNotFoundError:
        logger.error("Error: The student requests file %s was not found.", file_name)
        return None
    except IOError as e:
        logger.error("Error: An I/O error occurred: %s", e)
        return None

def load_available_seats(file_name: str) -> set[str]|None:
    """
    Loads the available seats to assign from file.
    
    Args:
        file_name (str): The filename for the available seats file. There should be one
                         seat name per row.
    
    Returns:
        set[str]: A set of strings representing the available seats. Duplicate seats are ignored.
    """

    available_seats: set[str]= set()
    try:
        with open(file_name, "r") as file:
            for seat in file:
                seat = seat.strip()
                available_seats.add(seat)
            return available_seats
    except FileNotFoundError:
        logger.error("The available seats file %s was not found.", file_name)
        return None
    except IOError as e:
        logger.error("Error: An I/O error occurred: %s", e)
        return None
    
def assign_seats(available_seats: set[str], student_requests: dict[str, list[str]]) -> dict[str, str]:
    """
    Assigns seats based on student requests. Student are selected from the dictionary at random, and their seats are assigned
    by using the ranked list that is the value in the dictionary. If no seat can be assigned, the student is placed in a holding
    queue until all other students are assigned.
    Args:
        available_seats (set[str]): A set of strings representing available seats
        student_requests (dict[str, list[str]]): A dictionary where students are the keys and the values are a 
                                                ranked list of preferred seats.

    Returns:
        dict[str,str]: a dictionary of seat assignments available seats to student names
    """
    seat_assignments: dict[str, str] = {}

    # make a copy of the parameters
    seats: list[str] = list(available_seats.copy())
    students: list[str] = list(student_requests.keys())
    holding: list[str] = []

    while seats and students:
        # grab a random student
        student: str = random.choice(students)
        logger.debug("Assigning %s.", student)
        for seat in student_requests[student]:
            logger.debug("Considering %s.", seat)
            # if the seat hasn't been assigned, assign the seat and remove 
            # the seat and student from consideration
            if seat in seats:
                logger.debug("Available - assigning.")
                seat_assignments[seat] = student
                seats.remove(seat)
                students.remove(student)
                break
            logger.debug("Already assigned.")
        
        # if we get here, and the student is still in the
        # list of students, then put them in holding
        if student in students:
            logger.debug("All requests considered - added to holding.")
            holding.append(student)
            students.remove(student)

    # if we ran out of seats early, add them to holding - they will not be assigned seats
    if students:
        holding += students
    
    # deal with any held students
    for student in holding:
        if seats:
            seat = random.choice(seats)
            seat_assignments[seat] = student
            seats.remove(seat)
            logger.debug("Assigned %s from holding to %s.", student, seat)
        else:
            logger.warning("No seats available to assign to %s.", student)

    return seat_assignments

def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    # read in command line args
    if len(sys.argv) < 2 or sys.argv[1] == "":
        logger.error("No seat file was specified.")
        return
    seat_file: str = sys.argv[1]


    if len(sys.argv) < 3 or sys.argv[2] == "":
        logger.error("No request file was specified.")
        return    
    request_file: str = sys.argv[2]

    available_seats: set[str]|None = load_available_seats(seat_file)
    
    # quit if loading the available seats failed
    if available_seats is None:
        return
    
    student_requests: dict[str, list[str]]|None = load_student_requests(request_file, available_seats)
    # quit if the  loading the student requests failed
    if student_requests is None:
        return

    if len(available_seats) < len(student_requests):
        logger.warning("There are only %d seats for %d students.", len(available_seats), len(student_requests))
    
    seat_assignments: dict[str, str] = assign_seats(available_seats, student_requests)
    # print out 
    for seat in sorted(seat_assignments.keys(), key=int):
        print(f"{seat}: {seat_assignments[seat]}")


if __name__ == "__main__":
    main()