import cv2
from flask import Flask, render_template, Response , redirect , url_for , request , session
import time
import numpy as np
import face_recognition
from Data.script import PersonDataManager , train , Person 
from sklearn.neighbors import NearestNeighbors
import os 
import random
import string 
from entities.course import Course , CourseDBManager , CoursePersonDBManager
from datetime import datetime, timedelta

weekdays = ["monday" ,  "tuesday" , "wednesday" , "thursday" , "friday" , "saturday" , "sunday"]
def lower(string) : 
    return string.lower() 

def get_today_courses() : 
    today = datetime.today().weekday() 
    courses = []
    for course in courseDbManager.get_all() : 
        if course.day == weekdays[today] : 
            courses.append(course) 
    return courses



def get_current_course():
    current_time = datetime.now().time()  # Get the current time
    courses = [] 
    
    for course in courseDbManager.get_all():
        try:
            course_time = datetime.strptime(course.hour, "%H:%M:%S").time()
            start_time = (datetime.combine(datetime.today(), current_time) - timedelta(minutes=10)).time()
            end_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()
            
            if start_time <= course_time <= end_time:
                courses.append(course)
        except ValueError as e:
            print(f"Error parsing course time: {course.hour}. Error: {e}")
    return courses

def convert_to_date_dict(data):
    result = {}
    for entry in data:
        date = datetime.strptime(entry['date']  , "%Y-%m-%d %H:%M:%S.%f").date()
        person_id = entry['person_id'] 
        
        if date not in result:
            result[date] = []
        
        result[date].append(personDbManager.get_person_by_id(person_id) )
    return result


app = Flask(__name__, template_folder="./templates")

isStreaming = False 
image_count = 0
database_path = "./data/database.db"

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

courseDbManager = CourseDBManager(database_path)
personDbManager = PersonDataManager() 
attendanceDbManager = CoursePersonDBManager(database_path)

persons = personDbManager.get_data()
persons_names = list(map(lower , personDbManager.get_names() )) 
persons_face_embeddings_dict = personDbManager.get_embeddings()
persons_ids =  list(persons_face_embeddings_dict.keys())
persons_face_embeddings = np.array(list(persons_face_embeddings_dict.values()))

nn = NearestNeighbors(n_neighbors=1)
nn.fit(persons_face_embeddings)  # Fit the model with the face data

cap = None 
def generate_frames( cam_role , person=None , course_id=None) : 
    global image_count , cap ,isStreaming 

    while isStreaming : 
        success , frame = cap.read() 
        if not success : 
            print("error to read image") 
        else : 
            gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray) 
            faces = face_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    x1, y1 = max(x - 30, 0), max(y - 30, 0)
                    x2, y2 = min(x + w + 30, frame.shape[1]), min(y + h + 30, frame.shape[0])
                    face_region = frame[y1:y2, x1:x2]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    if cam_role == "detect": 
                        face_region_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)

                        encodings = face_recognition.face_encodings(face_region_rgb)
                        if len(encodings) > 0:
                            encoded_image = encodings[0]

                            # Use NearestNeighbors to find the closest match
                            distances, indices = nn.kneighbors([encoded_image])

                            personName = "unknown"
                            if distances[0][0] < 0.4:  # Adjust threshold for similarity (0.3 is just an example)
                                person_id = persons_ids[indices[0][0]] 
                                person = personDbManager.get_person_by_id(person_id)
                                personName = person.name 
                                if person.role != 'TEACHER' : 
                                
                                    if not attendanceDbManager.attendance_verified(course_id , person_id) : 
                                        attendanceDbManager.add(course_id , person_id)
                                    
                            cv2.putText(frame, personName, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (200, 200, 10), 2)
                    elif cam_role == "take_pics" : 
                        if person : 
                            if image_count < 20:
                                filename = "".join(random.choices(string.ascii_letters, k=5)) + ".jpg"
                                folder = os.path.join(os.getcwd(), "data", person.name )
                                os.makedirs(folder, exist_ok=True)
                                cv2.imwrite(os.path.join(folder, filename), face_region)
                                image_count += 1 
                                cv2.putText(frame , str(image_count) , (600 , 30) , cv2.FONT_HERSHEY_SIMPLEX, 1.1, (200, 200, 10), 2)
                            else : 
                                cv2.putText(frame , "you can stop now!" , (400 , 30) , cv2.FONT_HERSHEY_SIMPLEX, 1.1, (200, 200, 10), 2) 
            _ , buffer = cv2.imencode(".jpg" , frame ) 
            frame = buffer.tobytes() 
        yield(b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
    if person  and cam_role == "take_pics" :  
        image_count = 0 
        with open(os.path.join(os.path.join(os.getcwd(), "Data", person.name ) , "info.txt") , "w") as file: 
            file.write(person.name +","+person.age+","+person.gender+","+person.role) 


@app.get("/")
def index() : 
    alert_text = request.args.get("message", default="")
    alert_type = request.args.get("type", default="")
    return render_template("index.html", courses=get_today_courses() ,  alert_text=alert_text, alert_type=alert_type )


@app.get("/detect")
def detect():
    course_id = request.args.get("course_id")
    
    if len(get_today_courses()) > 0 and len(get_current_course()) > 0 : 
        global isStreaming 
        global cap 

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video capture.")
            exit(1)
        time.sleep(0.5)
        isStreaming = True 
        return render_template("detect.html" , course_id=course_id)
    else : 
        return redirect(url_for("index" , message="no courses today or now" , type="danger"))


@app.get("/video_feed")
def video_feed():
    global cap 
    global isStreaming 
    role = request.args.get("role") 
    name = request.args.get("name") 
    age = request.args.get("age") 
    gender = request.args.get("gender")
    cam_role = request.args.get("cam_role") 
    course_id = request.args.get("course_id") 
    person = None 
    try : 
        if name and age and gender and role : 
            person = Person(None, name , age ,gender ,role ,None  )
        return Response(generate_frames(cam_role , person , course_id) , mimetype="multipart/x-mixed-replace; boundary=frame")
    except Exception : 
        print("error occured")

@app.get("/take_pics") 
def take_pics() : 
    global isStreaming 
    global cap 

    name = request.args.get("name" , default='No Precise').lower()
    age = request.args.get("age" , default=None)
    gender = request.args.get("gender" , default='Not Precise').upper() 
    role = request.args.get("role" , default='STUDENT').upper()
    if name not in persons_names : 
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video capture.")
            exit(1)
        time.sleep(1.0)
        isStreaming = True 
        return render_template("take_pics.html" , name = name , age=age , gender=gender , role=role)
    else : 
        return redirect(url_for("index" , message="the person already exist in the dataset" , type="danger"))


@app.get("/retrain")
def retrain() : 
    global persons 
    global persons_names 
    global persons_face_embeddings_dict 
    global persons_ids 
    global persons_face_embeddings
    global nn 
      # Fit the model with the face data
    try:
        # Train the model
        train() 
        persons = personDbManager.get_data()
        persons_names = list(map(str.lower, personDbManager.get_names()))  
        persons_face_embeddings_dict = personDbManager.get_embeddings()
        persons_ids = list(persons_face_embeddings_dict.keys())
        persons_face_embeddings = np.array(list(persons_face_embeddings_dict.values()))
    
        nn.fit(persons_face_embeddings)
        return redirect(url_for("index", message="The model retrained successfully", type="success"))
    
    except Exception as e:
        return redirect(url_for("index", message=f"An error occurred: {str(e)}", type="danger"))

@app.get("/stop") 
def stop() : 
    global isStreaming 
    global cap 
    isStreaming = False 
    cap.release()
    return redirect(url_for("index"))

@app.get("/persons") 
def show_persons() : 
    return render_template("persons.html" , persons=persons )

@app.get("/addPerson")
def addPerson() : 
    return render_template("addPerson.html" ) 

@app.get("/courses") 
def show_courses() : 
    courses = courseDbManager.get_all() 
    return render_template("courses.html" , courses = courses )

@app.get("/addCourse")
def addCourse() : 
    print(personDbManager.get_teachers())
    return render_template("addCourse.html", teachers=personDbManager.get_teachers() , weekdays=weekdays)

@app.get("/addCourseToDb") 
def addCourseToDb() : 
    name = request.args.get("name") 
    hour = request.args.get("hour")
    hour = f"{hour}:00"
    day = request.args.get("day") 
    teacher_id = request.args.get("teacher_id")  
    if name and hour and day and teacher_id : 
        course = Course(None , name , day , hour , teacher_id )
        courseDbManager.add_course(course) 
    return redirect(url_for("index" , message="the course added successfully" , type="success"))
@app.get("/attendance") 
def attendance() : 
    course_id = request.args.get("course_id") 
    if course_id  : 
        attended_persons = attendanceDbManager.get_all_by_course_id(course_id)
        attended_persons_dict = convert_to_date_dict(attended_persons) 
        return render_template("attendance.html" ,  data=attended_persons_dict)
    else :
        return redirect(url_for("index" , message="error" , type="danger"))
if __name__ == "__main__":

    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Cleanup resources
        cap.release()
        cv2.destroyAllWindows()
