import os
import openpyxl
import resend

from datetime import datetime

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI()


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# TEMPLATES
# =========================================================

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# CONFIGURATION
# =========================================================

EXCEL_FILE = "visitors.xlsx"

# Email where YOU receive contact-form submissions
RECEIVER_EMAIL = "ihtisham191181@gmail.com"

# Resend configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# For testing with Resend
SENDER_EMAIL = os.getenv(
    "RESEND_FROM_EMAIL",
    "onboarding@resend.dev"
)


# =========================================================
# INITIALIZE EXCEL
# =========================================================

def init_excel():

    if not os.path.exists(EXCEL_FILE):

        workbook = openpyxl.Workbook()

        sheet = workbook.active

        sheet.title = "Contacts"

        sheet.append([
            "Date/Time",
            "Name",
            "Email",
            "WhatsApp",
            "Message"
        ])

        workbook.save(EXCEL_FILE)

        workbook.close()

        print("visitors.xlsx created successfully.")


init_excel()


# =========================================================
# SAVE CONTACT TO EXCEL
# =========================================================

def save_to_excel(
    submitted_at: str,
    name: str,
    email: str,
    whatsapp: str,
    message: str
):

    workbook = openpyxl.load_workbook(
        EXCEL_FILE
    )

    sheet = workbook.active

    sheet.append([
        submitted_at,
        name,
        email,
        whatsapp,
        message
    ])

    workbook.save(
        EXCEL_FILE
    )

    workbook.close()


# =========================================================
# CHECK RESEND CONFIGURATION
# =========================================================

def check_email_configuration():

    if not RESEND_API_KEY:

        raise ValueError(
            "RESEND_API_KEY environment variable is missing."
        )

    resend.api_key = RESEND_API_KEY


# =========================================================
# SEND ADMIN NOTIFICATION EMAIL
# =========================================================

def send_contact_email(
    name: str,
    email: str,
    whatsapp: str,
    message: str,
    submitted_at: str
):

    check_email_configuration()

    email_body = f"""
NEW PORTFOLIO CONTACT SUBMISSION

============================================

SUBMISSION TIME

{submitted_at}

============================================

CONTACT DETAILS

Name:
{name}

Email:
{email}

WhatsApp:
{whatsapp}

============================================

PROJECT / MESSAGE

{message}

============================================

This message was submitted through
Ihtisham Mujahid's portfolio website.

Visitor Email:
{email}
"""

    params = {
        "from": SENDER_EMAIL,
        "to": [RECEIVER_EMAIL],
        "reply_to": email,
        "subject": f"New Portfolio Contact - {name}",
        "text": email_body
    }

    response = resend.Emails.send(params)

    return response


# =========================================================
# SEND CONFIRMATION EMAIL TO VISITOR
# =========================================================

def send_confirmation_email(
    name: str,
    visitor_email: str
):

    check_email_configuration()

    confirmation_body = f"""
Hi {name},

Thank you for contacting Ihtisham Mujahid.

Your message has been received successfully.

We will get back to you soon.

Best regards,

Ihtisham Mujahid
AI Automation Engineer
"""

    params = {
        "from": SENDER_EMAIL,
        "to": [visitor_email],
        "reply_to": RECEIVER_EMAIL,
        "subject": "Thanks for contacting Ihtisham Mujahid",
        "text": confirmation_body
    }

    response = resend.Emails.send(params)

    return response


# =========================================================
# HOME
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# =========================================================
# ABOUT
# =========================================================

@app.get(
    "/about",
    response_class=HTMLResponse
)
async def about(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="about.html"
    )


# =========================================================
# PROJECTS
# =========================================================

@app.get(
    "/projects",
    response_class=HTMLResponse
)
async def projects(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="projects.html"
    )


# =========================================================
# CONTACT PAGE
# =========================================================

@app.get(
    "/contact",
    response_class=HTMLResponse
)
async def contact(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="contact.html"
    )


# =========================================================
# CONTACT FORM SUBMISSION
# =========================================================

@app.post(
    "/contact",
    response_class=HTMLResponse
)
async def save_contact(

    request: Request,

    name: str = Form(...),

    email: str = Form(...),

    whatsapp: str = Form(...),

    message: str = Form(...)

):

    # -----------------------------------------------------
    # CLEAN INPUT
    # -----------------------------------------------------

    name = name.strip()
    email = email.strip()
    whatsapp = whatsapp.strip()
    message = message.strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not name:

        return templates.TemplateResponse(

            request=request,

            name="contact.html",

            context={
                "error_msg":
                    "Please enter your name."
            },

            status_code=400
        )


    if not email:

        return templates.TemplateResponse(

            request=request,

            name="contact.html",

            context={
                "error_msg":
                    "Please enter your email address."
            },

            status_code=400
        )


    if not whatsapp:

        return templates.TemplateResponse(

            request=request,

            name="contact.html",

            context={
                "error_msg":
                    "Please enter your WhatsApp number."
            },

            status_code=400
        )


    if not message:

        return templates.TemplateResponse(

            request=request,

            name="contact.html",

            context={
                "error_msg":
                    "Please tell me about your project."
            },

            status_code=400
        )


    # -----------------------------------------------------
    # CURRENT DATE / TIME
    # -----------------------------------------------------

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # =====================================================
    # SAVE TO EXCEL
    # =====================================================

    try:

        save_to_excel(
            submitted_at=current_time,
            name=name,
            email=email,
            whatsapp=whatsapp,
            message=message
        )

        print(
            f"Contact saved to Excel: {name}"
        )


    except Exception as excel_error:

        print(
            "EXCEL ERROR:",
            str(excel_error)
        )

        return templates.TemplateResponse(

            request=request,

            name="contact.html",

            context={
                "error_msg":
                    "Something went wrong while saving your message. "
                    "Please try again."
            },

            status_code=500
        )


    # =====================================================
    # SEND NOTIFICATION EMAIL TO YOU
    # =====================================================

    admin_email_sent = False

    try:

        admin_response = send_contact_email(
            name=name,
            email=email,
            whatsapp=whatsapp,
            message=message,
            submitted_at=current_time
        )

        admin_email_sent = True

        print(
            f"Admin notification sent successfully for: {name}"
        )

        print(
            "Resend admin response:",
            admin_response
        )


    except Exception as email_error:

        print(
            "ADMIN EMAIL ERROR:",
            str(email_error)
        )


    # =====================================================
    # SEND THANK-YOU EMAIL TO VISITOR
    # =====================================================

    confirmation_email_sent = False

    try:

        confirmation_response = send_confirmation_email(
            name=name,
            visitor_email=email
        )

        confirmation_email_sent = True

        print(
            f"Confirmation email sent successfully to: {email}"
        )

        print(
            "Resend confirmation response:",
            confirmation_response
        )


    except Exception as confirmation_error:

        print(
            "CONFIRMATION EMAIL ERROR:",
            str(confirmation_error)
        )


    # =====================================================
    # TERMINAL STATUS
    # =====================================================

    print("--------------------------------------")
    print(f"Contact: {name}")
    print(f"Admin email: {admin_email_sent}")
    print(
        f"Visitor confirmation: "
        f"{confirmation_email_sent}"
    )
    print("--------------------------------------")


    # =====================================================
    # SUCCESS RESPONSE
    # =====================================================

    success_message = (
        "Thank you! Your message was received successfully. "
        "I'll get back to you soon."
    )


    return templates.TemplateResponse(

        request=request,

        name="contact.html",

        context={
            "success_msg": success_message
        }

    )


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )