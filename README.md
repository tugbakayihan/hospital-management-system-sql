# Hospital Management System 

## Description 

This is a **Hospital Management System** project built with **Python (Flask microframework)**, **HTML**, **CSS**, and **PostgreSQL**.  
The system helps hospitals and administrators **efficiently manage and organize data** such as patients, doctors, departments, medical examinations, and bills.


## Software Requirements
- Python 3.10 or higher
- Flask 
- psycopg2
- PostgreSQL
- Jinja2 
- Web Browser

## Recommended Development Tools
- Visual Studio Code (IDE)
- pgAdmin (PostgreSQL GUI)

## How to Install and Run the Project

### 1. Install Python
If Python is not already installed:

- Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)  
- Click the **“Download Python 3.10+”** button (e.g., Python 3.12.x)  
- On the installation screen, **check the box that says “Add Python to PATH”**   
- Click **“Install Now”** to start the installation
---

### 2. Install Visual Studio Code

- Go to [https://code.visualstudio.com/](https://code.visualstudio.com/)
- Click on the **Download for Windows / macOS / Linux** button depending on your operating system
- Open the downloaded installer and follow the setup wizard  
   - You can use the **default installation options**
   - It is recommended to **check the option “Add to PATH”** during installation if prompted
- Once installed, launch **Visual Studio Code**
---

### 3. Add the Python Extension to VS Code

- To enable Python support in VS Code:
- Open Visual Studio Code
- Click the Extensions icon on the left sidebar (or press Ctrl + Shift + X)
- In the search bar, type Python
- Find the extension published by Microsoft and click Install

### 4. Download the Project Files

- Just download the project as a **.zip file**, extract it, and open the folder.

### 5. Install Python Dependencies

- Open Visual Studio Code and open the "hospital_app" folder, navigate through app.py in the folder, open the terminal or command prompt in "app.py" inside the project directory and run:

```bash
pip install Flask psycopg2
```

### 5. Set Up PostgreSQL

If PostgreSQL is not installed:

- Download and install it from: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
- During setup, choose a **username** and **password** (e.g., `postgres` / `your_password`)
- Open **pgAdmin** 
---

#### Restore from `.backup` File 

Used the provided `.backup` file:

1. Open **pgAdmin**
2. Log in and expand the **Servers** section
3. Click on PostgreSQL 17 and enter your password.
4. Right-click on **Databases** → **Create** → **Database**
5. Name the database exactly:
   ```
   Hospital_Management_System(1.1)
   ```
6. Click **Save** to create it
7. Right-click to the newly created database → **Restore**
8. In the dialog:
   - Set **Format** to `Custom or tar`
   - Select the provided `.backup` file for the filename part
   - On the Query Options Tab, click on "Clean before restore" to enable.
   - Click **Restore**

>  If you encounter errors during restore (e.g., active sessions, relation exists, permission denied), open the **Query Tool** and run the following commands to clean the schema before retrying:

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'Hospital_Management_System(1.1)'
  AND pid <> pg_backend_pid();

DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

After running these, **repeat the restore process again**.

---

If you still encounter a "failed" error after completing these steps, click on the schema and check the tables, then review the columns and constraints. If rows are present and everything appears correctly set, you can proceed to run the Flask application.


---

### 6. Run the Flask Application

Follow these steps to run the project using Visual Studio Code:

1. Open **Visual Studio Code**  
2. Click on **File → Open Folder**, and select the `hospital_app` folder  
3. Open the `app.py` file inside the project directory  
4. Make sure the database credentials in `app.py` match your PostgreSQL login. Write your own password and port number:

    ```python
    dbname="Hospital_Management_System(1.1)",
    user="postgres",
    password="your_password",
    host="localhost",
    port="your_portnumber"
    ```

5. Open a new terminal in Visual Studio Code  
6. In the terminal, if you are not under the hospital_app directory(it should look something like --> "PS C:\Users\ROG\Desktop\SQL PROJECT\SQL PROJECT\hospital_app>) you must navigate to the project folder by typing:

    ```bash
    cd .\hospital_app\
    ```
cd
7. Start the Flask server by running:

    ```bash
    python app.py
    ```

8. If the server starts successfully without errors, you will see output similar to:

    ```
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    ```

9. Open your browser and go to:

    ```
    http://localhost:5000
    ```


---

### 7.Open the App in Your Browser

Go to your browser and visit:


http://localhost:5000


You will be redirected to the **homepage**, where you can view and manage patient records.

Below are the main sections of the application and how to access them directly:

-  **Patients**:  
  `http://localhost:5000/`  
  (Default homepage — add, search, edit, and delete patients)

-  **Hospitals**:  
  `http://localhost:5000/hospitals`  
  (Manage hospital records such as name, address, city)

-  **Departments**:  
  `http://localhost:5000/departments`  
  (Create and assign departments to hospitals)

-  **Doctors**:  
  `http://localhost:5000/doctor`  
  (Manage doctor info and department assignment)

-  **Bills**:  
  `http://localhost:5000/bills`  
  (Add, update, delete, and view billing information related to examinations)

-  **Medical Examinations**:  
  `http://localhost:5000/medical_examination`  
  (Add and manage patient examination records, including links to doctors and departments)



## How to Use the Project

After running the project and visiting `http://localhost:5000`, you can navigate through the application and manage records in the following sections:

###  Patients
- Displays a list of all registered patients.
- You can **add a new patient**, **search by name**, or **edit/delete** existing records.
- When you click the **Edit** button, the input fields become editable for that patient.

###  Hospitals
- Visit `/hospitals` to manage hospital data.
- You can **add a new hospital**, **search**, **edit**, or **delete** existing records.
- Each hospital has a **name**, **address**, and **city** field.
- Clicking the **Edit** button will activate edit mode for that row.

###  Departments
- Go to `/departments` to create and manage departments.
- You can **add a new department**, **search by name**, or **delete** departments.
- Each department must be assigned to a specific hospital.

###  Doctors
- Visit `/doctor` to manage doctor records.
- You can **add**, **edit**, or **delete** doctors.
- Each doctor is linked to a department.

###  Medical Examinations
- Go to `/medical_examination` to manage patient examination records.
- You can **create a new examination** by selecting a patient, doctor, and department.
- Enter the **date** and **diagnosis** to complete the record.

###  Bills
- Visit `/bills` to manage billing information.
- You can **add**, **update**, **delete**, or **view** bills linked to examination records.
- Specify the **amount**, **payment status** (Paid/Unpaid), and **payment date**.


## Limitations

- **Lack of Authentication and Authorization**  
  The application does not include a user authentication system. All users can access, modify, and delete data without restrictions.

-  **No File Upload Capability**  
  Uploading or managing files such as medical reports, images, or documents is not supported in the current version.

-  **Limited Responsiveness**  
  The user interface has not been fully optimized for mobile or tablet devices and is best viewed on desktop browsers.

-  **Basic Form Validation**  
  The system performs only minimal input validation. It does not check for specific formats (e.g., email), nor does it handle duplicate or missing entries extensively.

-  **Insufficient Error Handling**  
  The application lacks detailed error messages for common issues, such as database connection failures or missing data inputs.

-  **Local Use Only**  
  The system is intended to run on a local machine. It is not configured for deployment to a production server or for handling multiple concurrent users.

-  **Date Restriction on Medical Examinations**  
  Examination records can only be created with a date that is **today or in the past**.  
  Attempting to enter a **future examination date** will result in a database error due to the constraint:  
  `CHECK (examination_date <= CURRENT_DATE)`.


## Credits
This project was developed by:

- Cemre Ece Beyazgül
- Tuğba Kayıhan
- Elif Bensu Koral
- Aybüke Kuruyüz

