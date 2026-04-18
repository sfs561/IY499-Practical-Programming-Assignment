from database import create_tables, add_patient, add_doctor, get_all_patients, get_all_doctors

def main():
    create_tables()

    add_patient("Batuhan", 22, "07123456789")
    add_doctor("Dr Smith", "Cardiology")

    print("Patients:")
    print(get_all_patients())

    print("Doctors:")
    print(get_all_doctors())

if __name__ == "__main__":
    main()