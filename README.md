🎓 AI-Based Student Attendance System (Flask)

🧠 About the System

This is an AI-based Student Attendance System built with Flask that uses facial recognition to automate and secure attendance tracking.

✅ Key Features

•⁠  ⁠High Accuracy: The system uses 128-dimensional face embeddings and a KNN model, delivering high-precision recognition even with similar faces.
•⁠  ⁠Real-Time Detection: Detects and recognizes students live via webcam.
•⁠  ⁠Retrainable Model: You can easily add new students, and the system will retrain the KNN model to include them.
•⁠  ⁠Scalable & Lightweight: Suitable for small to medium-sized classrooms; works well with limited hardware.
•⁠  ⁠Two-layered Storage:
  - XML file: Stores the 128-value face embeddings per student.
  - SQLite DB: Stores course , and attendance records.


---

🧠 How It Works

1.⁠ ⁠Student Registration  
   - student takes a photo .  
   - System extracts a 128-dimension face embedding and stores it in an XML file.

2.⁠ ⁠Recognition / Attendance  
   - Capture a face image.  
   - The embedding is extracted and compared using KNN to existing embeddings.  
   - If a match is found, attendance is marked.

---

🛠️ Tech Stack
 ---------------------------------------
| Layer      | Technology               |
|------------|--------------------------|
| Backend    | Python + Flask           |
| Face       |  face_recognition ⁠       |
| Embedding  |                          |
| ML Model   | K-Nearest Neighbors (KNN)|
| Storage    | XML for face data        |
| Frontend   | HTML, CSS, JS            |
 ---------------------------------------

📂 Sample XML Structure

⁠ xml
<Faces>
	<Face>
		<ID>
			1
		</ID>
		<PersonName>
			Mohamed el afia
		</PersonName>
		<Age>
			20
		</Age>
		<Gender>
			MALE
		</Gender>
		<Role>
			STUDENT
		</Role>
		<EmbeddingValues>
			<Value0>
				-0.14117948959271112
			</Value0>
			...
        </EmbeddingValues>
    </Face>
    ...
<Faces>

---

📸 Frontend Features

•⁠  ⁠Register new student (upload image)
•⁠  ⁠Take attendance (real-time or image upload)
•⁠  ⁠View attendance history
•⁠  ⁠Admin-friendly interface

---

🗂️ Data Storage

•⁠  ⁠Face Embeddings: Stored in an XML file (128-dimensional vectors for each registered student).
•⁠  ⁠Course & Attendance Data: Stored in a SQLite database:
  - Tables:
    - ⁠ courses ⁠ – list of available courses.
    - ⁠ attendance ⁠ – records of attendance with timestamps and recognized names.

---

📌 Future Enhancements

•⁠  ⁠Admin login/authentication
•⁠  ⁠Export attendance reports (CSV/PDF)

