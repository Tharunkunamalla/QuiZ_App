# Quiz App

This is a Quiz Application built using Python, Tkinter for the GUI, MySQL for the database, and various other libraries for additional functionalities like email sending and PDF generation.

## Overview

The Quiz App allows users to select a category and the number of questions they want to answer. After completing the quiz, users can generate a report of their performance, which can be sent to their email.

## Features

- Select quiz category and number of questions
- Answer multiple-choice questions
- View score and feedback for each question
- Generate a performance report in PDF format
- Send the report via email

## Prerequisites

- Python 3.x
- MySQL Server

## Setup Instructions

### 1. Create a Virtual Environment

```sh
python -m venv venv
```

### 2. Activate the Virtual Environment

- On Windows:

  ```sh
  venv/Scripts/activate
  ```

- On macOS/Linux:

  ```sh
  source venv/bin/activate
  ```

### 3. Install Required Libraries

```sh
pip install -r requirements.txt
```

### 4. Add Secrets in `.env` File

- Ensure MySQL server is running.
- Create a `.env` file in the root directory with the following content:
  ```env
  SENDER_PASSWORD=your_email_password
  SENDER_EMAIL=your_email@example.com
  DB_PASSWORD=your_mysql_password
  ```

### 5. Run the Application

```sh
python quiz_app.py
```

## Usage

1. Select a quiz category.
2. Choose the number of questions.
3. Answer the questions.
4. View your score and feedback.
5. Generate and send the performance report via email.