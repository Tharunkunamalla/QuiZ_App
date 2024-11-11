import mysql.connector as ms
import tkinter as tk
from tkinter import font
import time
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from tkinter import messagebox
from dotenv import load_dotenv
import emoji

load_dotenv()

def create():
    conn = ms.connect(host='localhost',user='root',password=os.getenv("DB_PASSWORD"))
    cursor = conn.cursor()
    with open("create_script.sql", "r") as file:
        sql = file.read()
        for statement in sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
    conn.commit()
    conn.close()
    print("Database Created Successfully")

# checking if the database exists
conn = ms.connect(host='localhost',user='root',password=os.getenv("DB_PASSWORD"))
cursor = conn.cursor()
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()
database_exists = False
for database in databases:
    if 'quiz_questions' in database:
        database_exists = True
        break

if not database_exists:
    print("Database 'Quiz_Questions' not found. Creating ... ")
    create()


# Establishing the connection
conn = ms.connect(host='localhost',
                  user='root',
                  password=os.getenv('DB_PASSWORD'),
                  database='Quiz_Questions')

cursor = conn.cursor()

# Global variables to track the current question index, score, and answers
question_index = 0
score = 0
correct_count = 0
incorrect_count = 0
start_time = 0  # For tracking quiz start time

# Function to get questions based on the category and number of questions & in a random order 
def get_questions(category, num_questions):
    query = "SELECT question_text, option1, option2, option3, option4, correct_answer FROM questions WHERE category = %s ORDER BY RAND() LIMIT %s"
    cursor.execute(query, (category, num_questions))
    questions = cursor.fetchall()
    
    # Debugging print to check if questions are being fetched correctly
    print(f"Fetched {len(questions)} questions for category '{category}'")

    return questions

#function for checking email validity
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def send_email_with_report(to_email, report_path, feedback_label):
    from_email = os.getenv("SENDER_EMAIL")  # Replace with actual email
    from_password = os.getenv("SENDER_PASSWORD")  # Replace with the actual password (use environment variables or a config file for security)
    subject = "Your Quiz Report"
    
    # Creating the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    body = """Please find attached your quiz report. 
Thank you for taking the quiz 💗!

With regards,
Quiz App Team
    """
    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF report
    try:
        with open(report_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(report_path)}")
        msg.attach(part)

        # Sending the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        feedback_label.config(text="Report sent successfully!", fg="Blue")

    except Exception as e:
        feedback_label.config(text=f"Failed to send email: {str(e)}", fg="red")


# Gradient creation function
def create_gradient(canvas, width, height, color1, color2):
    # Create a vertical gradient (light pink to white)
    for i in range(height):
        # Calculate the intermediate color for each pixel row
        r1, g1, b1 = canvas.winfo_rgb(color1)
        r2, g2, b2 = canvas.winfo_rgb(color2)
        r = int(r1 + (r2 - r1) * i / height)
        g = int(g1 + (g2 - g1) * i / height)
        b = int(b1 + (b2 - b1) * i / height)
        
        # Set the color to hex
        color = f'#{r:02x}{g:02x}{b:02x}'
        
        # Draw a line for the gradient
        canvas.create_line(0, i, width, i, fill=color, width=1)


# Function to start the quiz and load questions
def start_quiz(category, num_questions):
    global question_index, score, correct_count, incorrect_count, start_time,end_time,options_selected
    score = 0
    question_index = 0
    correct_count = 0
    incorrect_count = 0
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Record the quiz start time
    options_selected = dict()  # Dictionary to store the selected options for each question

    questions = get_questions(category, num_questions)

     # To Check if questions are available
    if not questions:
        print("No questions found. Please check the database.")
        feedback_label.config(text="No questions available for this category.", fg="red")
        return

    def load_question(index,selected_option=None):
        global options_selected
        var.set(selected_option)
        if 0 <= index < len(questions):
            question_data = questions[index]
            question_text, opt1, opt2, opt3, opt4, correct_ans = question_data
            question_label.config(text=question_text)
            option1_radio.config(text=opt1, value=opt1)
            option2_radio.config(text=opt2, value=opt2)
            option3_radio.config(text=opt3, value=opt3)
            option4_radio.config(text=opt4, value=opt4)
            feedback_label.config(text="")

            if selected_option:
                submit_button.config(state=tk.DISABLED)
            else:
                submit_button.config(state=tk.NORMAL)

        # Update the score label on each question load
            score_label.config(text=f"Score: {score}/{len(questions)}")

        else:
            feedback_label.config(text=f"Quiz completed! Your score: {score}/{len(questions)}", fg="Blue")
            score_label.config(text=f"Final Score: {score}/{len(questions)}")
            submit_button.config(state=tk.DISABLED)
            next_button.config(state=tk.DISABLED)
            back_button.config(state=tk.DISABLED)
            generate_report_button.pack()  # Show the report generation button

    def submit_answer():
        global score, correct_count, incorrect_count, options_selected
        #var object accessing get() function of the StringVar class 👇
        selected_option = var.get()  
        correct_answer = questions[question_index][5]
        options_selected[question_index]=selected_option

        if selected_option == correct_answer:
            score += 1
            correct_count += 1
            feedback_label.config(text="Correct!", fg="Blue")
        else:
            incorrect_count += 1
            feedback_label.config(text=f"Incorrect! The correct answer is: {correct_answer}", fg="red")

        # Update the score label after submission
        score_label.config(text=f"Score: {score}/{len(questions)}")

        submit_button.config(state=tk.DISABLED)
        

    def next_question():
        global question_index, options_selected
        if question_index < len(questions) - 1:
            question_index += 1
            selected_option = options_selected.get(question_index)
            load_question(question_index, selected_option)
            # submit_button.config(state=tk.NORMAL)
        else:
            feedback_label.config(text=f"Quiz completed! Your score: {score}/{len(questions)}", fg="Blue")
            score_label.config(text=f"Final Score: {score}/{len(questions)}")
            submit_button.config(state=tk.DISABLED)
            next_button.config(state=tk.DISABLED)
            back_button.config(state=tk.DISABLED)
            generate_report_button.pack()  # Show the report generation button when quiz ends


    def previous_question():
        global question_index, options_selected
        if question_index > 0:
            question_index -= 1
            selected_option = options_selected.get(question_index)
            load_question(question_index, selected_option)
            # submit_button.config(state=tk.DISABLED)
        else:
            feedback_label.config(text="You are on the first question.", fg="blue")

    # Function to generate the quiz report
    def generate_report():
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Record the quiz end time
        # Calculate the time taken as a duration in seconds
        time_taken = (time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")) - 
              time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")))

        # Create pie chart
        labels = ['Correct', 'Incorrect']
        sizes = [correct_count, incorrect_count]
        colors = ['#4CAF50', '#FF6347']
        explode = (0.1,0.1)
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, explode=explode ,labels=labels, colors=colors, autopct='%1.1f%%', shadow = True,startangle=140)
        
        plt.title("Test Analysis")
        plt.axis('equal')
        chart_path = 'quiz_chart.png'
        plt.savefig(chart_path)
        plt.close()

        # Generate a unique file name for the report
        report_path = f'quiz_report.pdf'
        
        # Create PDF report
        pdf = FPDF()
        pdf.add_page()
        # pdf.set_font("Arial", size=12)

        # Set the title with bold and underline formatting
        pdf.set_font("Arial", "BU", 16)  # Bold and underlined
        pdf.set_fill_color(200, 220, 255)  # Light blue color for the header
        pdf.cell(0, 10, txt="Quiz Report", ln=True, align="C")

        # Leave some space
        pdf.ln(5)

        # Set font for table headers (bold)
        pdf.set_font("Arial", "B", 12)

        # Table headers
        pdf.cell(80, 10, txt="Details", border=1, align="C")
        pdf.cell(110, 10, txt="Values", border=1, align="C")
        pdf.ln(10)  # Move to the next line

        # Set font for table content (regular)
        pdf.set_font("Arial", "", 12)

        # For creating report cells 👇 
        fields = [
            ("Category", category),
            ("Total Score", f"{score}/{len(questions)}"),
            ("Correct Answers", correct_count),
            ("Incorrect Answers", incorrect_count),
            ("Start Time", start_time),
            ("Finish Time", end_time),
            ("Time Taken", f"{time_taken:.2f} seconds")
        ]

        for i, (field, detail) in enumerate(fields):
            # Alternate color for rows
            if i % 2 == 0:
                pdf.set_fill_color(230, 240, 255)  # Light color for even rows
            else:
                pdf.set_fill_color(255, 255, 255)  # White for odd rows

            # Create cells with the fill color
            pdf.cell(80, 10, txt=field, border=1, ln=0, fill=True)
            pdf.cell(110, 10, txt=str(detail), border=1, ln=1, fill=True)

        # Adding a line break after the table 
        pdf.ln(10)

        #Add a table for options selected by user & correct answers
        pdf.set_font("Arial", "BU", 12)
        pdf.cell(0, 10, txt="Question-wise Analysis", ln=True, align="C")
        pdf.ln(5)
        
        # Set the font for the table headers
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, txt="Question", border=1, align="C")
        pdf.cell(50, 10, txt="Selected Option", border=1, align="C")
        pdf.cell(50, 10, txt="Correct Answer", border=1, align="C")
        pdf.ln(10)

        # Set the font for the table content
        pdf.set_font("Arial", "", 12)

        for i, question in enumerate(questions):
            question_text = question[0]
            correct_answer = question[5]
            selected_option = options_selected.get(i, "Not answered")
            pdf.cell(80, 10, txt=question_text, border=1, align="L")
            pdf.cell(50, 10, txt=selected_option, border=1, align="C")
            pdf.cell(50, 10, txt=correct_answer, border=1, align="C")
            pdf.ln(10)

        table_y = pdf.get_y()
        pdf.ln(30)  # Leave some space after the table

        pdf.set_y(table_y+10)
        pdf.image(chart_path, x=10, y=pdf.get_y(), w=90)
        pdf.output(report_path)
        
        #deleting the png of pie chart
        if os.path.exists(chart_path):
            os.remove(chart_path)

        feedback_label.config(text=f"Report generated: {report_path}", fg="blue")

         # Email validation and sending report
        email = tk.simpledialog.askstring("Email Address", "Enter your email address to receive the report:")
        if not is_valid_email(email):
            feedback_label.config(text="Invalid email format. Please enter a correct email.", fg="red")
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
        else:
            send_email_with_report(email, report_path, feedback_label)
        
        # deleting the pdf file
        if os.path.exists(report_path):
            os.remove(report_path)

        
    root = tk.Tk()
    root.title("Quiz App")
    root.geometry("1920x1118")
    # root.configure(bg="lightblue")
    # Create a canvas for the gradient background
    canvas = tk.Canvas(root, width=1920, height=1118)
    canvas.pack(fill="both", expand=True)

    # Call the create_gradient function to create the gradient effect
    create_gradient(canvas, 1920, 1118, "#FFB6C1", "#FFFFFF")  # Light pink to white gradient
    
    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    question_font = font.Font(family="Arial", size=14)
    option_font = font.Font(family="Arial", size=12)
    button_font = font.Font(family="Arial", size=12, weight="bold")

    question_label = tk.Label(canvas, text="", font=question_font)
    question_label.pack(pady=(20, 20))

    # StringVar is a class, var is an object of that class 
    var = tk.StringVar(value="None of the options... Select one")
    option_frame = tk.Frame(canvas, bg="#f0f8ff")
    option_frame.pack()


    option1_radio = tk.Radiobutton(option_frame, variable=var, font=option_font, text="", bg="#f0f8ff", activebackground="#f0f8ff",value='1')
    option2_radio = tk.Radiobutton(option_frame, variable=var, font=option_font, text="", bg="#f0f8ff", activebackground="#f0f8ff",value='2')
    option3_radio = tk.Radiobutton(option_frame, variable=var, font=option_font, text="", bg="#f0f8ff", activebackground="#f0f8ff",value='3')
    option4_radio = tk.Radiobutton(option_frame, variable=var, font=option_font, text="", bg="#f0f8ff", activebackground="#f0f8ff",value='4')

    option1_radio.pack(anchor="w", pady=5)
    option2_radio.pack(anchor="w", pady=5)
    option3_radio.pack(anchor="w", pady=5)
    option4_radio.pack(anchor="w", pady=5)

    # root.bind('<Key>', select_option_by_key)
 
    feedback_label = tk.Label(canvas, text="", font=button_font, bg="#ffc6cf")
    feedback_label.pack(pady=10)

    # Create a label to display the current score
    score_label = tk.Label(canvas, text=f"Score: {score}/{len(questions)}", font=button_font, bg="#ffc9d1")
    score_label.pack(pady=10)

    submit_button = tk.Button(canvas, text="Submit", command=submit_answer, font=button_font, bg="#ffa07a", fg="white")
    submit_button.pack(pady=10)

    next_button = tk.Button(canvas, text="Next", command=next_question, font=button_font, bg="#4682b4", fg="white")
    next_button.pack(side="right", padx=20, pady=10)

    back_button = tk.Button(canvas, text="Go Back", command=previous_question, font=button_font, bg="#4682b4", fg="white")
    back_button.pack(side="left", padx=20, pady=10)

    generate_report_button = tk.Button(canvas, text="Get Report", command=generate_report, font=button_font, bg="#00CED1", fg="white")
    generate_report_button.pack_forget()  # Initially hidden until quiz is completed

    load_question(question_index)

    root.mainloop()

def select_question_number(category):
    number_window = tk.Tk()
    number_window.title("Select Number of Questions")
    number_window.geometry("400x300")
    number_window.configure(bg="#C9E9D2")

    label_font = font.Font(family="Helvetica", size=14, weight="bold")
    button_font = font.Font(family="Arial", size=12)

    tk.Label(number_window, text="Choose Number of Questions", font=label_font, bg="#f5f5f5", fg="navy").pack(pady=20)

    question_numbers = [5, 10, 15, 20]

    def handle_selection(num_questions):
        number_window.destroy()
        start_quiz(category, num_questions)

    for num in question_numbers:
        button = tk.Button(number_window, text=f"{num} Questions", font=button_font, bg="#FFE3E3", fg="black", width=20, command=lambda n=num: handle_selection(n))
        button.pack(pady=10)

    number_window.mainloop()

def select_category():
    category_window = tk.Tk()
    category_window.title("Select Quiz Category")
    category_window.geometry("400x300")
    category_window.configure(bg="#C9E9D2")

    label_font = font.Font(family="Helvetica", size=14, weight="bold")
    button_font = font.Font(family="Arial", size=12)

    tk.Label(category_window, text="Choose a Category", font=label_font, bg="#f5f5f5", fg="navy").pack(pady=20)

    categories = ["Mathematics", "Science", "Geography", "Literature"]

    for category in categories:
        button = tk.Button(category_window, text=category, font=button_font, bg="#FFDDC1", fg="black", width=20, command=lambda c=category: [category_window.destroy(), select_question_number(c)])
        button.pack(pady=10)

    category_window.mainloop()


def display_instructions():
    instructions_window = tk.Tk()
    instructions_window.title("Quiz Instructions")
    instructions_window.geometry("1059x873")
    instructions_window.configure(bg="#C9E9D2")

    instructions_label = tk.Label(instructions_window, text=emoji.emojize("""
    Welcome to the Quiz App!:party_popper:

    Please read the instructions carefully before starting :scroll:
    
    1. Select a category from the list. :books:
    2. Choose the number of questions you'd like to attempt. :input_numbers:
    3. Answer the questions and get feedback on each answer. :check_mark_button:
    4. At the end of the quiz, you will be able to generate a report with your score. :bar_chart:
    5. You can also receive the report via email. :envelope_with_arrow:
    6. Be careful you can submit the answers only once. :warning:
    7. You need to submit after selecting option to update score.
    8. You can go back to the an unattempted question by using "Go Back" button. :backhand_index_pointing_left:
    
    All the Best :thumbs_up: , and enjoy the quiz! :four_leaf_clover: :four_leaf_clover:"""),font=("Segoe UI Emoji", 12), bg="#f5f5f5",justify="left")
    instructions_label.pack(pady=20, padx=10)

    # Start Quiz Button
    start_button = tk.Button(instructions_window, text="Start Quiz", font=("Arial", 14), bg="#00CED1", fg="white", command=lambda: [instructions_window.destroy(), select_category()])
    start_button.pack(pady=20)

    instructions_window.mainloop()

display_instructions()
conn.close()