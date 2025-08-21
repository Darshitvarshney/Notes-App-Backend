
# Collaborative Notes Backend

## 📌 Project Overview
This project provides the backend for a **collaborative notes application**.  
The system allows authenticated users to **create, edit, tag, and share notes**.  

Key features:
- User authentication & authorization
- Admins can invite collaborators to work together
- Notes can be tagged and organized

---

## ⚙️ Tech Stack
- **Python 3.x**
- **Flask** (backend framework)
- **MongoDB** (database)
- **JWT** (authentication)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Darshitvarshney/Notes-App-Backend.git
cd Notes-App-Backend

```

### 2. Create & Activate Virtual Environment
It’s recommended to use a virtual environment to isolate project dependencies.

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux / Mac)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. I could Create a Environment Variables File (.env)
But didn't did it so that you can run it easily

### 5. Run the Application
```bash
python app.py
```


## 🧪 API Documentation
A **Postman collection** is provided for easy testing of the APIs.  


👉 [Postman Collection Link](https://darshitvarshney-8750718.postman.co/workspace/NotesApp~1bc03347-5dfe-4c54-bc67-cefc89ad96f0/collection/47681806-908fde07-cb70-47cc-b7d2-b4f927e52fa3?action=share&source=copy-link&creator=47681806)

---

## 👥 Collaborators
- Admin users can invite other users to workspaces.
- Notes support tagging, editing, and sharing between collaborators.

---

## 📂 Project Structure (example)
```
.
├── backend/                  # Main application package
│   ├── models/           # MongoEngine models
│   ├── routes/           # API routes
│   ├── utils/            # Helper functions
├── requirements.txt
├── app.py                # Entry point
└── README.md
```

---

## ✅ Next Steps ((Cannot do because of Time constraint))
- Implement optional **note versioning**  
- Add **search with natural language queries**  
- Improve collaboration features

---
