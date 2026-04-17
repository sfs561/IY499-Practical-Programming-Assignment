from database import create_tables, add_patient, get_all_patients

def main():
    create_tables()
    add_patient("Batuhan", 22, "07123456789")
    print(get_all_patients())

if __name__ == "__main__":
    main()