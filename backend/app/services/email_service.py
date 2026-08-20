import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

def send_violation_email(to_email: str, violation_details: dict, evidence_path: str = None):
    if not SENDGRID_API_KEY:
        print("SendGrid API key not set. Skipping email.")
        return False
        
    message = Mail(
        from_email='noreply@smarthelmet.local',
        to_emails=to_email,
        subject=f"Traffic Violation Detected: {violation_details.get('violation_type')}",
        html_content=f"""
        <strong>Violation Details</strong>
        <ul>
            <li>Type: {violation_details.get('violation_type')}</li>
            <li>Location: {violation_details.get('location_lat')}, {violation_details.get('location_lon')}</li>
            <li>Time: {violation_details.get('violation_timestamp')}</li>
            <li>Confidence: {violation_details.get('confidence_score')}</li>
        </ul>
        """
    )
    
    if evidence_path and os.path.exists(evidence_path):
        with open(evidence_path, 'rb') as f:
            data = f.read()
            encoded_file = base64.b64encode(data).decode()
            
        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName(os.path.basename(evidence_path)),
            FileType('application/octet-stream'),
            Disposition('attachment')
        )
        message.attachment = attachedFile

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
