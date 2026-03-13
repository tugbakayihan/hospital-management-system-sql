from flask import *
import psycopg2
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
error = ""

# PostgreSQL bağlantısı
conn = psycopg2.connect(
    dbname="Hospital_Management_System(1.1)",
    user="postgres",
    password="HaydarAli06",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# -------------------- PATIENT --------------------

@app.route('/', methods=['GET'])
def index():
    global error
    if error:
        flash(f"❌ Error: {error}", category="error")
        error = ""

    search_query = request.args.get('search', '')
    edit_id      = request.args.get('edit')     


    if search_query:
        cursor.execute("""
            SELECT * FROM patient
            WHERE firstname ILIKE %s OR lastname ILIKE %s
            ORDER BY patientid
        """, (f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("SELECT * FROM patient ORDER BY patientid")

    rows = cursor.fetchall()

 
    patients = []
    today = date.today()
    for r in rows:
        birthdate = r[3]
        age = today.year - birthdate.year - (
            (today.month, today.day) < (birthdate.month, birthdate.day)
        )
        patients.append({
            'id'       : r[0],
            'firstname': r[1],
            'lastname' : r[2],
            'age'      : age,
            'gender'   : r[4],
            'phonenumber'    : r[5],
            'birthdate': birthdate,   
        })

   
    selected_patient = next(
        (p for p in patients if str(p['id']) == str(edit_id)),
        None
    )

    return render_template(
        'index.html',
        patients=patients,
        selected_patient=selected_patient,
        search_query=search_query
    )

@app.route('/submit_patient', methods=['POST'])
def submit_patient():
    patientid   = request.form.get('patientid')          
    firstname   = request.form['firstname'].strip()
    lastname    = request.form['lastname'].strip()
    birthdate   = request.form['birthdate']              # yyyy-mm-dd
    gender      = request.form['gender']
    phonenumber = request.form['phonenumber'].strip()

    try:
        if patientid:                                    # ---------- UPDATE ----------
            cursor.execute("""
                UPDATE patient SET
                    firstname   = %s,
                    lastname    = %s,
                    birthdate   = %s,
                    gender      = %s,
                    phonenumber = %s
                 WHERE patientid = %s
            """, (firstname, lastname, birthdate, gender, phonenumber, patientid))
            flash("✅ Patient updated successfully!", "success")

        else:                                            # ---------- INSERT ----------
           
            cursor.execute("SELECT nextval('patientid_seq')")
            new_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO patient (patientid, firstname, lastname, birthdate, gender, phonenumber)
                     VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_id, firstname, lastname, birthdate, gender, phonenumber))
            flash(f"✅ Patient added successfully! (ID: {new_id})", "success")

        conn.commit()

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "error")

    return redirect('/')

@app.route('/delete/<int:patientid>')
def delete(patientid):
    try:
        cursor.execute("DELETE FROM patient WHERE patientid = %s", (patientid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Silme işlemi sırasında hata:", e)
    return redirect('/')

# -------------------- BILL --------------------


@app.route('/bills', methods=['GET'])
def bills():
    global error
    if error:
        flash(f"❌ Error: {error}", "error")
        error = ""

    search_query = request.args.get('search', '')
    edit_id      = request.args.get('edit')


    if search_query.isdigit():
        cursor.execute("""
            SELECT * FROM bill
             WHERE billid = %s
             ORDER BY billid
        """, (int(search_query),))
    else:
        cursor.execute("""
            SELECT * FROM bill
            ORDER BY billid
        """)

    rows = cursor.fetchall()
    bills            = []
    selected_bill    = None
    today            = date.today()   

    for b in rows:
        raw_paymentdate = b[3]

        
        if isinstance(raw_paymentdate, str):
       
            try:
                paymentdate_obj = datetime.strptime(raw_paymentdate[:10], '%Y-%m-%d')
            except ValueError:
                paymentdate_obj = None
        elif hasattr(raw_paymentdate, 'strftime'):  
            paymentdate_obj = raw_paymentdate
        else:
            paymentdate_obj = None

        formatted_date = (
            paymentdate_obj.strftime('%Y-%m-%d') if paymentdate_obj
            else str(raw_paymentdate)[:10]       # fallback
        )

        bill_dict = {
            'billid'       : b[0],
            'totalamount'  : b[1],
            'paymentstatus': b[2],
            'paymentdate'  : formatted_date,
            'examinationid': b[4]
        }
        bills.append(bill_dict)

        # ✏️ Edit modundaki satırı bul
        if edit_id and str(b[0]) == edit_id:
            selected_bill = bill_dict

    return render_template(
        'bill.html',
        bills=bills,
        selected_bill=selected_bill,
        search_query=search_query
    )


# ------------------------------------------------------
@app.route('/submit_bill', methods=['POST'])
def submit_bill():
    billid        = request.form.get('billid')           
    totalamount   = float(request.form['totalamount'])
    paymentstatus = request.form['paymentstatus']
    paymentdate   = request.form['paymentdate']
    examinationid = int(request.form['examinationid'])

    try:
        if paymentstatus not in ('Paid', 'Unpaid', 'Pending'):
            raise ValueError("Ödeme durumu Paid, Unpaid veya Pending olmalı.")

        if billid:                                       # ---------- UPDATE ----------
            cursor.execute("""
                UPDATE bill SET
                    totalamount   = %s,
                    paymentstatus = %s,
                    paymentdate   = %s,
                    examinationid = %s
                 WHERE billid = %s
            """, (totalamount, paymentstatus,
                  paymentdate, examinationid, billid))
            flash("✅ Bill updated successfully!", "success")

        else:                                            # ---------- INSERT ----------
            cursor.execute("SELECT nextval('billid_seq')")
            new_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO bill (billid, totalamount, paymentstatus, paymentdate, examinationid)
                     VALUES (%s, %s, %s, %s, %s)
            """, (new_id, totalamount, paymentstatus, paymentdate, examinationid))
            flash(f"✅ Bill added successfully! (ID: {new_id})", "success")

        conn.commit()

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "error")

    return redirect('/bills')


@app.route('/delete_bill/<int:billid>')
def delete_bill(billid):
    try:
        cursor.execute("DELETE FROM bill WHERE billid = %s", (billid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error deleting bill: {e}", "error")

    return redirect('/bills')

# -------------------- HOSPITAL --------------------

@app.route('/hospitals', methods=['GET'])
def hospitals():
    global error
    if error:
        flash(f"❌ Error: {error}", "error")
        error = ""

    search_query = request.args.get('search', '')
    edit_id      = request.args.get('edit')


    if search_query:
        cursor.execute("""
            SELECT * FROM hospital
             WHERE hospitalname ILIKE %s
                OR city ILIKE %s
             ORDER BY hospitalid
        """, (f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("""
            SELECT * FROM hospital
            ORDER BY hospitalid
        """)

    rows = cursor.fetchall()
    hospitals = [{
        'hospitalid'  : r[0],
        'hospitalname': r[1],
        'address'     : r[2],
        'city'        : r[3],
        'phonenumber' : r[4]
    } for r in rows]

    selected_hospital = next(
        (h for h in hospitals if str(h['hospitalid']) == str(edit_id)),
        None
    )

    return render_template(
        'hospital.html',
        hospitals=hospitals,
        selected_hospital=selected_hospital,
        search_query=search_query
    )


@app.route('/submit_hospital', methods=['POST'])
def submit_hospital():
    hospitalid = request.form.get('hospitalid')          
    name       = request.form['hospitalname'].strip()
    address    = request.form['address'].strip()
    city       = request.form['city'].strip()
    phone      = request.form['phonenumber'].strip()

    try:
        if hospitalid:                                   # ---------- UPDATE ----------
            cursor.execute("""
                UPDATE hospital SET
                    hospitalname = %s,
                    address      = %s,
                    city         = %s,
                    phonenumber  = %s
                 WHERE hospitalid = %s
            """, (name, address, city, phone, hospitalid))
            flash("✅ Hospital updated successfully!", "success")

        else:                                            # ---------- INSERT ----------
            
            cursor.execute("SELECT nextval('hospitalid_seq')")
            new_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO hospital (hospitalid, hospitalname, address, city, phonenumber)
                     VALUES (%s, %s, %s, %s, %s)
            """, (new_id, name, address, city, phone))
            flash(f"✅ Hospital added successfully! (ID: {new_id})", "success")

        conn.commit()

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "error")

    return redirect('/hospitals')




@app.route('/delete_hospital/<int:hospitalid>')
def delete_hospital(hospitalid):
    try:
        cursor.execute("DELETE FROM hospital WHERE hospitalid = %s", (hospitalid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Hospital silme hatası:", e)
    return redirect('/hospitals')

# -------------------- DEPARTMENT --------------------

@app.route('/departments', methods=['GET'])
def departments():
    global error
    if error != "":
        flash(f"❌ Error: {str(error)}", category="error")
        error = ""

    search_query = request.args.get('search', '')
    edit_id      = request.args.get('edit')  

    if search_query:
        cursor.execute("""
            SELECT * FROM department
             WHERE deptname ILIKE %s
             ORDER BY departmentid          -- <-- SIRALAMA
        """, ('%' + search_query + '%',))
    else:
        cursor.execute("""
            SELECT * FROM department
             ORDER BY departmentid          -- <-- SIRALAMA
        """)

    rows = cursor.fetchall()
    departments = [{
        'departmentid': row[0],
        'deptname'    : row[1],
        'hospitalid'  : row[2]
    } for row in rows]


    selected_department = next(
        (d for d in departments if str(d['departmentid']) == str(edit_id)),
        None
    )

    return render_template(
        'department.html',
        departments=departments,
        selected_department=selected_department,
        search_query=search_query
    )



@app.route('/submit_department', methods=['POST'])
def submit_department():
    departmentid = request.form.get('departmentid')          
    deptname     = request.form['deptname'].strip()
    hospitalid   = int(request.form['hospitalid'])

    try:
        if departmentid:                                     # ---------- UPDATE ----------
            cursor.execute("""
                UPDATE department
                   SET deptname   = %s,
                       hospitalid = %s
                 WHERE departmentid = %s
            """, (deptname, hospitalid, departmentid))
            flash("✅ Department updated successfully!", "success")

        else:                                                # ---------- ADD ----------
           
            cursor.execute("SELECT nextval('departmentid_seq')")
            new_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO department (departmentid, deptname, hospitalid)
                     VALUES (%s, %s, %s)
            """, (new_id, deptname, hospitalid))
            flash(f"✅ Department added successfully! (ID: {new_id})", "success")

        conn.commit()

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "error")

    return redirect('/departments')




@app.route('/delete_department/<int:departmentid>/<int:hospitalid>')
def delete_department(departmentid, hospitalid):
    try:
        cursor.execute("""
            DELETE FROM department
            WHERE departmentid = %s AND hospitalid = %s
        """, (departmentid, hospitalid))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Department silme hatası:", e)
    return redirect('/departments')



# ------------------- DOCTOR ----------------------

@app.route('/doctor', methods=['GET'])
def doctor():
    global error
    if error != "":
        flash(f"❌ Error: {str(error)}", category="error")
        error = ""

    search_query = request.args.get('search', '')
    edit_id = request.args.get('edit')

    if search_query:
        cursor.execute("""
            SELECT * FROM doctor
            WHERE drfirstname ILIKE %s OR drlastname ILIKE %s OR specialization ILIKE %s
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("SELECT * FROM doctor ORDER BY doctorid ASC")

    rows = cursor.fetchall()
    doctors = [{
        'doctorid': row[0],
        'firstname': row[1],
        'lastname': row[2],
        'yearsofexperience': row[3],
        'specialization': row[4],
        'phonenumber': row[5],
        'departmentid': row[6]
    } for row in rows]

    selected_doctor = None
    if edit_id:
        for d in doctors:
            if str(d['doctorid']) == edit_id:
                selected_doctor = d
                break

    return render_template('doctor.html', doctors=doctors, selected_doctor=selected_doctor, search_query=search_query)


@app.route('/submit_doctor', methods=['POST'])
def submit_doctor():
    doctorid = request.form.get('doctorid')

    firstname = request.form['firstname']
    lastname = request.form['lastname']
    specialization = request.form['specialization']
    yearsofexperience = int(request.form['yearsofexperience'])
    phonenumber = request.form['phonenumber']
    departmentid = int(request.form['departmentid'])

    try:
        if doctorid:
            # UPDATE
            cursor.execute("""
                UPDATE doctor SET
                    drfirstname = %s,
                    drlastname = %s,
                    specialization = %s,
                    yearsofexperience = %s,
                    drphonenumber = %s,
                    departmentid = %s
                WHERE doctorid = %s
            """, (firstname, lastname, specialization, yearsofexperience, phonenumber, departmentid, doctorid))
            flash("✅ Doctor updated successfully!", "success")
        else:
            # ADD
            cursor.execute("SELECT nextval('doctor_doctorid_seq')")
            new_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO doctor (doctorid, drfirstname, drlastname, specialization, yearsofexperience, 
                                    drphonenumber, departmentid)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (new_id, firstname, lastname, specialization, yearsofexperience, phonenumber, departmentid))
            flash("✅ Doctor added successfully!", "success")

        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {str(e)}", "error")

    return redirect('/doctor')


@app.route('/delete_doctor/<int:doctorid>')
def delete_doctor(doctorid):
    try:
        cursor.execute("DELETE FROM doctor WHERE doctorid = %s", (doctorid,))
        conn.commit()
        flash("✅ Doctor deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {str(e)}", "error")
    return redirect('/doctor')

# ------------------- MEDICAL EXAMINATION ----------------------

@app.route('/examination', methods=['GET'])
def examination():
    global error
    if error:
        flash(f"❌ Error: {error}", "error")
        error = ""

    search_query = request.args.get('search', '')
    edit_id      = request.args.get('edit')


    if search_query:
        cursor.execute("""
            SELECT * FROM medical_examination
            WHERE CAST(examinationid AS TEXT) ILIKE %s
               OR diagnosis ILIKE %s
               OR prescription ILIKE %s
            ORDER BY examinationid
        """, (f'%{search_query}%',)*3)
    else:
        cursor.execute("SELECT * FROM medical_examination ORDER BY examinationid")

    rows = cursor.fetchall()
    examinations = [{
        'examinationid'  : r[0],
        'examinationdate': r[1],
        'diagnosis'      : r[2],
        'prescription'   : r[3],
        'doctorid'       : r[4],
        'patientid'      : r[5]
    } for r in rows]

    selected_examination = next(
        (e for e in examinations if str(e['examinationid']) == str(edit_id)),
        None
    )

    return render_template(
        'examination.html',
        examinations        = examinations,
        selected_examination = selected_examination,
        search_query        = search_query
    )

# ------------------------------------------------------

# ------------------------------------------------------
@app.route('/submit_examination', methods=['POST'])
def submit_examination():
    examinationid   = request.form.get('examinationid')  
    examinationdate = request.form['examinationdate']
    diagnosis       = request.form['diagnosis']
    prescription    = request.form['prescription']
    doctorid        = int(request.form['doctorid'])
    patientid       = int(request.form['patientid'])

    try:
        if examinationid:                                 # ---------- UPDATE ----------
            cursor.execute("""
                UPDATE medical_examination SET
                    examinationdate = %s,
                    diagnosis       = %s,
                    prescription    = %s,
                    doctorid        = %s,
                    patientid       = %s
                 WHERE examinationid = %s
            """, (examinationdate, diagnosis, prescription,
                  doctorid, patientid, examinationid))
            flash("✅ Examination updated successfully!", "success")

        else:                                             # ---------- INSERT ----------
            cursor.execute("SELECT nextval('examinationid_seq')")
            new_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO medical_examination
                    (examinationid, examinationdate, diagnosis, prescription, doctorid, patientid)
                 VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_id, examinationdate, diagnosis, prescription, doctorid, patientid))
            flash(f"✅ Examination added successfully! (ID: {new_id})", "success")

        conn.commit()

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {e}", "error")

    return redirect('/examination')


@app.route('/delete_examination/<int:examinationid>')
def delete_examination(examinationid):
    try:
        cursor.execute("DELETE FROM medical_examination WHERE examinationid = %s", (examinationid,))
        conn.commit()
        flash("✅ Examination deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {str(e)}", "error")
    return redirect('/examination')





# -------------------- APP --------------------

if __name__ == '__main__':
    app.run(debug=True)
