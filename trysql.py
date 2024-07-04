import pymysql

def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456',  # 更换为你的数据库密码
        db='student',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def initialize_db():
    """创建数据库和表结构"""
    db = connect_db()
    with db.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS student")
        cursor.execute("USE student")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                sno VARCHAR(10) NOT NULL,
                name VARCHAR(100) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                age INT,
                department VARCHAR(100),
                PRIMARY KEY (sno)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                cno VARCHAR(10) NOT NULL,
                cname VARCHAR(100) NOT NULL,
                PRIMARY KEY (cno)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                sno VARCHAR(10),
                cno VARCHAR(10),
                grade DECIMAL(5, 2),
                PRIMARY KEY (sno, cno),
                FOREIGN KEY (sno) REFERENCES students(sno),
                FOREIGN KEY (cno) REFERENCES courses(cno)
            )
        """)
        db.commit()
    db.close()

# 1）新生入学信息增加，学生信息修改。
def add_student():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            sql = "INSERT INTO students (sno, name, gender, age, department) VALUES (%s, %s, %s, %s, %s)"
            sno = input("Enter student number: ")
            name = input("Enter name: ")
            gender = input("Enter gender: ")
            age = input("Enter age: ")
            department = input("Enter department: ")
            cursor.execute(sql, (sno, name, gender, age, department))
            db.commit()
            print("Student added successfully.")
    finally:
        db.close()

def update_student():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            sno = input("Enter student number to update: ")

            # 获取当前学生的信息
            cursor.execute("SELECT * FROM students WHERE sno = %s", (sno,))
            current_data = cursor.fetchone()
            if not current_data:
                print("No student found with the provided student number.")
                return

            print(f"Current Information: {current_data}")

            # 用户选择要更新的信息
            name = input("Enter new name (leave blank to keep unchanged): ")
            gender = input("Enter new gender (leave blank to keep unchanged): ")
            age = input("Enter new age (leave blank to keep unchanged): ")
            department = input("Enter new department (leave blank to keep unchanged): ")

            # 构建更新SQL语句
            update_fields = []
            data_to_update = []

            if name:
                update_fields.append("name = %s")
                data_to_update.append(name)
            if gender:
                update_fields.append("gender = %s")
                data_to_update.append(gender)
            if age:
                update_fields.append("age = %s")
                data_to_update.append(age)
            if department:
                update_fields.append("department = %s")
                data_to_update.append(department)

            if not update_fields:
                print("No updates were made as no new information was provided.")
                return

            # 更新数据库
            update_query = "UPDATE students SET " + ", ".join(update_fields) + " WHERE sno = %s"
            data_to_update.append(sno)
            cursor.execute(update_query, tuple(data_to_update))
            db.commit()

            print("Student information updated successfully.")
    finally:
        db.close()


# 2）课程信息维护
def add_course():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            sql = "INSERT INTO courses (cno, cname) VALUES (%s, %s)"
            cno = input("Enter course number: ")
            cname = input("Enter course name: ")
            cursor.execute(sql, (cno, cname))
            db.commit()
            print("Course added successfully.")
    finally:
        db.close()

def update_course():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            cno = input("Enter course number to update: ")
            cname = input("Enter new course name: ")
            cursor.execute("UPDATE courses SET cname = %s WHERE cno = %s", (cname, cno))
            db.commit()
            print("Course updated successfully.")
    finally:
        db.close()

def delete_course():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            cno = input("Enter course number to delete: ")
            cursor.execute("DELETE FROM courses WHERE cno = %s AND cno NOT IN (SELECT cno FROM enrollments)", (cno,))
            db.commit()
            print("Course deleted successfully.")
    finally:
        db.close()

# 3）录入学生成绩，修改学生成绩
def add_grade():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            sno = input("Enter student number: ")
            cno = input("Enter course number: ")
            grade = input("Enter grade: ")
            sql = "INSERT INTO enrollments (sno, cno, grade) VALUES (%s, %s, %s)"
            cursor.execute(sql, (sno, cno, grade))
            db.commit()
            print("Grade added successfully.")
    finally:
        db.close()

def update_grade():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            sno = input("Enter student number: ")
            cno = input("Enter course number: ")
            grade = input("Enter new grade: ")
            cursor.execute("UPDATE enrollments SET grade = %s WHERE sno = %s AND cno = %s", (grade, sno, cno))
            db.commit()
            print("Grade updated successfully.")
    finally:
        db.close()

# 4）按系统计学生的平均成绩、最好成绩、最差成绩、优秀率、不及格人数
def calculate_statistics():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.department,
                    AVG(e.grade) AS average, 
                    MAX(e.grade) AS highest, 
                    MIN(e.grade) AS lowest,
                    SUM(CASE WHEN e.grade >= 90 THEN 1 ELSE 0 END) AS excellence_count,
                    SUM(CASE WHEN e.grade < 60 THEN 1 ELSE 0 END) AS fail_count,
                    COUNT(e.grade) AS total_count
                FROM enrollments e
                JOIN students s ON e.sno = s.sno
                GROUP BY s.department
            """)
            results = cursor.fetchall()

            if results:
                for result in results:
                    if result['total_count'] > 0:
                        excellence_rate = (result['excellence_count'] / result['total_count']) * 100
                        print(f"Department: {result['department']}")
                        print(f"  Average Grade: {result['average']:.2f}")
                        print(f"  Highest Grade: {result['highest']}")
                        print(f"  Lowest Grade: {result['lowest']}")
                        print(f"  Excellence Rate: {excellence_rate:.2f}%")
                        print(f"  Fail Count: {result['fail_count']}\n")
                    else:
                        print(f"Department: {result['department']} - No grade data available to calculate statistics.")
            else:
                print("No grade data available in any department.")
    finally:
        db.close()


# 5）按系对学生成绩进行排名，同时显示出学生、课程和成绩信息
def rank_by_department():
    """ 按部门和课程对学生成绩进行排名 """
    db = connect_db()
    try:
        with db.cursor() as cursor:
            # 查询每个学生的学号、系、姓名、课程名称和成绩，并按系、课程和成绩降序排列
            cursor.execute("""
                SELECT s.sno, s.department, s.name, c.cname, e.grade
                FROM enrollments e
                JOIN students s ON e.sno = s.sno
                JOIN courses c ON e.cno = c.cno
                ORDER BY s.department, c.cname, e.grade DESC
            """)
            results = cursor.fetchall()

            # 初始化排名和上一个记录的变量
            last_department = None
            last_course = None
            last_grade = None
            department_course_rank = 1  # 部门和课程内的排名

            # 格式化输出标题
            print(f"{'Department':15} | {'Course':15} | {'Student No':10} | {'Name':20} | {'Grade':6} | {'Rank':4}")
            print("-" * 80)  # 输出分隔线

            # 输出结果并计算排名
            for row in results:
                if row['department'] != last_department or row['cname'] != last_course:
                    # 如果部门或课程改变了，重置部门和课程内的排名
                    department_course_rank = 1
                    last_department = row['department']
                    last_course = row['cname']
                elif row['grade'] != last_grade:
                    # 如果成绩变了，在同一部门和课程内增加排名
                    department_course_rank += 1

                # 更新最后一个记录的成绩，为下一行比较做准备
                last_grade = row['grade']

                # 格式化输出每行数据
                print(f"{row['department']:15} | {row['cname']:15} | {row['sno']:10} | {row['name']:20} | {row['grade']:6} | {department_course_rank:4}")
    finally:
        db.close()


# 6）输入学号，显示该学生的基本信息和选课信息
def show_student_info():
    db = connect_db()
    try:
        with db.cursor() as cursor:
            sno = input("Enter student number: ")
            cursor.execute("SELECT * FROM students WHERE sno = %s", (sno,))
            student_info = cursor.fetchone()

            if student_info:
                # 格式化并输出学生基本信息
                print("\nStudent Information:")
                print(f"  Student Number: {student_info['sno']}")
                print(f"  Name: {student_info['name']}")
                print(f"  Gender: {student_info['gender']}")
                print(f"  Age: {student_info['age']}")
                print(f"  Department: {student_info['department']}")

                # 查询并输出学生的课程信息
                cursor.execute(
                    "SELECT c.cname, e.grade FROM enrollments e JOIN courses c ON e.cno = c.cno WHERE e.sno = %s",
                    (sno,))
                courses = cursor.fetchall()
                if courses:
                    print("\nCourses and Grades:")
                    for course in courses:
                        print(f"  Course: {course['cname']} - Grade: {course['grade']}")
                else:
                    print("  No course information available.")
            else:
                print("No student found with that student number.")

    finally:
        db.close()


# 主程序
def main():
    while True:
        print("""
        1. Add New Student
        2. Update Student Information
        3. Add New Course
        4. Update Course Information
        5. Delete Course
        6. Add Grade
        7. Update Grade
        8. Calculate Statistics
        9. Rank by Department
        10. Show Student Info
        11. Exit
        """)
        choice = int(input("Choose an option: "))
        if choice == 1:
            add_student()
        elif choice == 2:
            update_student()
        elif choice == 3:
            add_course()
        elif choice == 4:
            update_course()
        elif choice == 5:
            delete_course()
        elif choice == 6:
            add_grade()
        elif choice == 7:
            update_grade()
        elif choice == 8:
            calculate_statistics()
        elif choice == 9:
            rank_by_department()
        elif choice == 10:
            show_student_info()
        elif choice == 11:
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()