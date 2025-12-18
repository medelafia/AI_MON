from . import dbconnection 
from datetime import datetime , date 

class Course:
    def __init__(self, id, name, day, hour, teacher_id) -> None:
        self.id = id
        self.name = name
        self.day = day
        self.hour = hour
        self.teacher_id = teacher_id


class CourseDBManager:
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        with dbconnection.db_connection(self.db_path) as cursor:
            cmd = """CREATE TABLE IF NOT EXISTS course ( 
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        name TEXT, 
                        day TEXT, 
                        hour TEXT, 
                        teacher_id INT
                    );"""
            cursor.execute(cmd)

    def get_all(self):
        with dbconnection.db_connection(self.db_path) as cursor:
            data = []
            query = "SELECT * FROM course"
            cursor.execute(query)

            for row in cursor.fetchall():
                course = Course(int(row[0]), row[1], row[2], row[3], int(row[4]))
                data.append(course)
            return data

    def get_all_contains(self, search_key ) :
        with dbconnection.db_connection(self.db_path) as cursor:
            data = []
            query = "SELECT * FROM course WHERE name LIKE '%' || :search || '%'"
            cursor.execute(query , {"search" : search_key})

            for row in cursor.fetchall():
                course = Course(int(row[0]), row[1], row[2], row[3], int(row[4]))
                data.append(course)
            return data
    def add_course(self, course: Course):
        with dbconnection.db_connection(self.db_path, commit=True) as cursor:
            try:
                query = """INSERT INTO course (name, day, hour, teacher_id) 
                           VALUES (:name, :day, :hour, :teacher_id)"""
                cursor.execute(
                    query,
                    {
                        "name": course.name,
                        "day": course.day,
                        "hour": course.hour,
                        "teacher_id": course.teacher_id,
                    },
                )
                return cursor.lastrowid
            except Exception as ex:
                print(f"Error adding course: {str(ex)}")


class CoursePersonDBManager : 
    def __init__(self , db_path) -> None:
        self.db_path = db_path 
        self.create_table() 
    def create_table(self) : 
        with dbconnection.db_connection(self.db_path) as cursor : 
            cmd = """
                CREATE TABLE IF NOT EXISTS course_persons ( 
                    course_id INT, 
                    person_id INT, 
                    date TEXT, 
                    FOREIGN KEY (course_id) REFERENCES course(id)
                );
            """
            cursor.execute(cmd) 
        
    def add(self , course_id , person_id) : 
        with dbconnection.db_connection(self.db_path , commit=True) as cursor : 
            cmd = """
                INSERT INTO course_persons VALUES(:course_id , :person_id , :date ) ; 
            """
            cursor.execute(cmd , {
                "course_id" : course_id , "person_id" : person_id , "date" : datetime.now()
            })
    def get_all(self) : 
        with dbconnection.db_connection(self.db_path ) as cursor :
            cmd = """
                select * from course_persons ; 
            """
            data = []
            cursor.execute(cmd) 
            for row in cursor.fetchall() : 
                data.append({"course_id" : int(row[0]) , "person_id" : int(row[1]) , "date" : row[2]}) 
            return data 
    def get_all_by_course_id(self , course_id) : 
        with dbconnection.db_connection(self.db_path ) as cursor :
            cmd = """
                select * from course_persons where course_id=:course_id ; 
            """
            data = []
            cursor.execute(cmd , {"course_id" : course_id }) 
            for row in cursor.fetchall() : 
                data.append({"course_id" : int(row[0]) , "person_id" : int(row[1]) , "date" : row[2]}) 
            return data 
    def get_all_by_person_id(self , person_id) : 
        with dbconnection.db_connection(self.db_path ) as cursor :
            cmd = """
                select * from course_persons where person_id=:person_id ; 
            """
            data = []
            cursor.execute(cmd , {"person_id" : person_id }) 
            for row in cursor.fetchall() : 
                data.append({"course_id" : int(row[0]) , "person_id" : int(row[1]) , "date" : row[2]}) 
            return data 
    def attendance_verified(self , course_id , person_id ) : 
        with dbconnection.db_connection(self.db_path ) as cursor :
            cmd = """
                select * from course_persons where person_id=:person_id and course_id=:course_id; 
            """
            data = []
            cursor.execute(cmd , {"person_id" : person_id , "course_id" : course_id }) 
            if len(cursor.fetchall()) > 0  : 
                return True 
            return False