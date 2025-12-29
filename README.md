# Purple Housing 

Purple Housing is a **Django-based web application** developed using the **MVT (Model–View–Template)** architecture.

## Project Overview
This project is a **property management system** where:
- Users can view available properties
- Users can apply for properties
- The entire system is managed through the **Admin Panel**

## Key Features
- Built using Django MVT architecture
- Property listing system
- Property application system
- Admin approval and disapproval workflow
- Application fee deduction system
- Email notification system using Django Signals

## Property Application Workflow
- When a user applies for a property:
  - **$50 USD is automatically deducted**
  - The application status is set to **Pending**
  - An email notification is sent to both the **User and the Admin**

## Email Notifications (Signals)
- Django `signals.py` is used for email automation
- When a user submits a property application:
  - Both User and Admin receive an email  
    stating that the request has been received and is currently pending
- When the Admin:
  - **Approves** or
  - **Disapproves** the application  
  another email is sent including:
  - The updated status
  - The **message provided by the Admin** through a popup

## Admin Panel
- Add, update, and delete properties
- Manage user applications
- Approve or disapprove applications with a custom message
- Full control of the system through the Admin Panel

## Technologies Used
- Python
- Django
- HTML
- CSS
- JavaScript
- Django Signals
- MYSQL (as per configuration)

## Project Purpose
The purpose of Purple Housing is to implement a **real-world property approval workflow** with:
- Secure admin control
- Automated email notifications
- A user-friendly property application process

---

**Developed by:** Muhammad Hammad Arshad
