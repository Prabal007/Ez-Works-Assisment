# Secure File Sharing System

## Overview
A REST API for secure file sharing between Operations Users and Client Users. The system enforces strict role-based access and secure file downloads.

## Features
- **Operations User**:
  - Login
  - Upload files (pptx, docx, xlsx)
- **Client User**:
  - Sign up with email verification
  - Login
  - List all uploaded files
  - Download files via secure links

## Tech Stack
- **Backend Framework**: REST API
- **Database**: SQLite 
- **Authentication**: JWT
- **File Storage**: Local File System

# POSTMAN DUMP

#CURLS

1. curl --location 'http://127.0.0.1:5000/signup' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "abc",
    "password": "abc",
    "email": "sample_email@gmail.com",
    "ops_user": true
}'

2. curl --location 'http://127.0.0.1:5000/verify_email' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": “sample_email@gmail.com",
    "verification_code": "1517"
}'   

3. curl --location 'http://127.0.0.1:5000/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "sample_email@gmail.com",
    "password": "abc"
}' 

4. curl --location 'http://127.0.0.1:5000/upload' \
--header 'Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZXhwIjoxNzMxODU4Mjg0fQ.JfW591ATlp8DQasmxqz8JFymHsauAcPuyiC3JaYPzxo' \
--form 'file=@"/path/to/file"' 

5. curl --location --request POST 'http://127.0.0.1:5000//files/2/get-download-url' \
--header 'Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZXhwIjoxNzMxODU4Mjg0fQ.JfW591ATlp8DQasmxqz8JFymHsauAcPuyiC3JaYPzxo'

6. curl --location 'http://127.0.0.1:5000/download?token=570496a2-3a76-4c7d-9990-22662d7857a0'

7. curl --location 'http://127.0.0.1:5000/files' \
--header 'Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZXhwIjoxNzMxODYxOTMyfQ.Iy_QMrDMCKd69oQkCf6SGVLJn5h86XcI2yyCmQ99eHA'
