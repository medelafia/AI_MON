import cv2
import face_recognition
import numpy as np
from xml.etree.ElementTree import *
import os


data_path = os.path.join( os.getcwd() , "Data" ) 
# Load Haar Cascade XML file
haar_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


###################### student class and student data manager 
class Person : 
    def __init__(self , id , name , age , gender, role ,embeddings) -> None:
        self.id = id 
        self.name = name 
        self.age = age 
        self.gender = gender 
        self.role = role 
        self.embeddings = embeddings 
    def __str__(self) -> str:
        return self.name + " -> " + self.role 

class PersonDataManager: 
    def __init__(self) -> None:
        self.data = self.get_data()
    def get_data(self):
        self.data = []
        tree = parse(os.path.join("./Model/" , "file.xml") ) 
        root = tree.getroot()

        faces = root.findall('Face') 
        for face in faces:
            
            person_name = face.find('PersonName').text.strip()
            person_age = face.find("Age").text
            person_gender = face.find("Gender").text
            person_id = int(face.find("ID").text) 
            person_role = face.find("Role").text.strip()
            embedding_values = []
            embedding_values_elem = face.find('EmbeddingValues')
            for value_elem in embedding_values_elem:
                embedding_values.append(float(value_elem.text.strip()))

            person = Person(person_id , person_name , person_age , person_gender ,person_role ,embedding_values )
            self.data.append( person )
        return self.data
    def get_person_by_id(self , id ) : 
        for person in self.data : 
            if person.id == id : 
                return person
    def get_embeddings(self) : 
        embeddings = {} 
        for person in self.data : 
            embeddings[person.id] = person.embeddings
        return embeddings
    def get_names(self) : 
        names = []
        for person in self.data : 
            names.append(person.name) 
        return names 
    def get_teachers(self) : 
        teachers = []
        for person in self.data: 
            if person.role.upper() == "TEACHER" : 
                teachers.append(person) 
        return teachers 

# Function to save encoding to an XML file
def save_embedding_to_xml(embedding, filename, person ):
    tree = parse(filename)
    root = tree.getroot()
    face = SubElement(root, "Face")

    name = SubElement(face, "PersonName")
    id = SubElement(face , "ID" )
    age = SubElement(face , "Age") 
    gender = SubElement(face , "Gender")
    role = SubElement(face , "Role") 

    id.text = str(get_last_id() + 1)  
    name.text = person.name 
    gender.text = person.gender
    age.text = person.age 
    role.text = person.role 
    values = SubElement(face, "EmbeddingValues")
    for i, value in enumerate(embedding):
        element = SubElement(values, f"Value{i}")
        element.text = str(value)

    # Write to file
    tree = ElementTree(root)
    tree.write(filename, encoding="UTF-8", xml_declaration=True)




def get_avg(data):
    res = []
    num_rows = len(data)
    num_cols = 128  # Assuming all rows have the same number of columns

    for col_index in range(num_cols):
        col_sum = sum(row[col_index] for row in data)
        col_avg = col_sum / num_rows
        res.append(col_avg)

    return res
def clean_data() : 
    names = PersonDataManager().get_names() 
    folders = os.listdir(data_path)
    folders.remove("__pycache__") 
    for person_name in folders:
        person_path = os.path.join(data_path, person_name)
        if person_name in names and os.path.isdir(person_path):
            for file in os.listdir(person_path):
                file_path = os.path.join(person_path, file)
                if os.path.isfile(file_path): 
                    os.remove(file_path)

            os.rmdir(person_path)
            print(f"Deleted data for {person_name}")
        else:
            print(f"Cannot delete {person_name}. Train the model first or ensure the name exists.")

def get_last_id() : 
    ids = []
    tree = parse(os.path.join("./Model/" , "file.xml") ) 
    root = tree.getroot()

    faces = root.findall('Face') 
    for face in faces:
        id = int(face.find("ID").text) 
        ids.append(id) 
    return max(ids) 

def train():
    persons_names = PersonDataManager().get_names() 
    persons_in_data_dir = os.listdir(data_path)
    persons_in_data_dir.remove("__pycache__")
    persons_in_data_dir.remove("database.db")
    print("folders:" , persons_in_data_dir )
    if len(persons_in_data_dir)  == 0 : 
        print("no thing to update") 
        return 
    else :  
        print("training started")
    for personName in persons_in_data_dir : 
        if personName not in persons_names and os.path.isdir(os.path.join(data_path, personName)):
            print(personName)
            embeddings = []
            count = 0
            for image in os.listdir(os.path.join(data_path, personName)):
                if not image.endswith(".txt") : 
                    # Load image and convert to grayscale
                    image = cv2.imread(os.path.join(data_path, personName, image))
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                    faces = haar_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))

                    if len(faces) > 0:
                        image_center = np.array(
                            [image.shape[1] // 2, image.shape[0] // 2])
                        closest_face = min(faces, key=lambda rect: np.linalg.norm(
                            (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2) - image_center))
                        x, y, w, h = closest_face

                        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

                        face_rgb = cv2.cvtColor(image[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
                        try:
                            face_encoding = face_recognition.face_encodings(face_rgb)[0]
                            embeddings.append(face_encoding)
                            count += 1
                        except:
                            pass 
            if len(embeddings) > 0:
                res = get_avg(embeddings)
                person = Person(None , None , None , None , None , None ) 
                with open(os.path.join(data_path, personName, "info.txt") , "r") as file : 
                    line = file.readline()  # Read a line from the file
                    line = line.strip()  # Remove leading/trailing whitespace or newline characters
                    parts = line.split(",")
                    person.name = parts[0]
                    person.age = parts[1]
                    person.gender = parts[2]
                    person.role = parts[3] 
                save_embedding_to_xml(res, "./Model/file.xml", person)
                print(personName + " saved to xml")
                clean_data()
                return
                
            