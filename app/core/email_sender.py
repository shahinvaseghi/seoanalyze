"""
Email Sender Module for GSC Reports
Supports SMTP email sending with various providers
"""
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class EmailSender:
    """Email sender using SMTP"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize email sender with SMTP configuration
        
        Args:
            config_path: Path to SMTP config file (default: configs/smtp_config.json)
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'configs' / 'smtp_config.json'
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load SMTP configuration from JSON file"""
        try:
            if not self.config_path.exists():
                return {'enabled': False}
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if not config.get('enabled', False):
                return {'enabled': False}
            
            return config
        except Exception as e:
            print(f"Error loading SMTP config: {e}")
            return {'enabled': False}
    
    def is_enabled(self) -> bool:
        """Check if email sending is enabled"""
        return self.config.get('enabled', False)
    
    def send_report_email(
        self,
        to_email: str,
        report_data: Dict[str, Any],
        property_name: str = "Unknown Property"
    ) -> tuple[bool, str]:
        """
        Send GSC report via email
        
        Args:
            to_email: Recipient email address
            report_data: Report data dictionary
            property_name: Property name for subject
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_enabled():
            return False, "Email sending is not enabled. Please configure SMTP settings."
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.get('from_name', 'SEO Analyze Pro')} <{self.config.get('from_email')}>"
            msg['To'] = to_email
            msg['Subject'] = f"GSC Report - {property_name} - {report_data.get('period', 'Unknown Period')}"
            
            # Create email body
            html_body = self._create_html_report(report_data, property_name)
            text_body = self._create_text_report(report_data, property_name)
            
            # Attach both HTML and text versions
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Send email via SMTP
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port', 587)
            use_tls = self.config.get('use_tls', True)
            username = self.config.get('username')
            password = self.config.get('password')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls()
                
                server.login(username, password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed. Check username and password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    def _create_html_report(self, report_data: Dict[str, Any], property_name: str) -> str:
        """Create HTML email body"""
        period = report_data.get('period', 'Unknown')
        avg_position_change = report_data.get('avg_position_change', 0)
        reports = report_data.get('reports', {})
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; background: #f5f5f5; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
                h1 {{ color: #10b981; border-bottom: 2px solid #10b981; padding-bottom: 10px; }}
                h2 {{ color: #3b82f6; margin-top: 30px; }}
                .summary {{ background: #f0f9ff; padding: 20px; border-radius: 6px; margin: 20px 0; }}
                .summary-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }}
                .summary-item:last-child {{ border-bottom: none; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #e5e7eb; }}
                th {{ background: #f9fafb; font-weight: 600; color: #374151; }}
                .badge {{ padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
                .badge-positive {{ background: #10b981; color: white; }}
                .badge-negative {{ background: #ef4444; color: white; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📈 گزارشات Google Search Console</h1>
                <p><strong>Property:</strong> {property_name}</p>
                <p><strong>بازه زمانی:</strong> {period}</p>
                
                <div class="summary">
                    <h2>خلاصه گزارشات</h2>
                    <div class="summary-item">
                        <span>تغییر میانگین Position:</span>
                        <strong>{avg_position_change:+.2f}</strong>
                    </div>
                    <div class="summary-item">
                        <span>دوره قبلی:</span>
                        <span>{report_data.get('previous_period', 'N/A')}</span>
                    </div>
                    <div class="summary-item">
                        <span>دوره فعلی:</span>
                        <span>{report_data.get('current_period', 'N/A')}</span>
                    </div>
                </div>
        """
        
        # Add report sections
        if reports.get('high_impressions_zero_clicks'):
            html += """
                <h2>⚠️ صفحات با Impression بالا ولی 0 Click</h2>
                <table>
                    <tr><th>صفحه</th><th>Impressions</th><th>Position</th></tr>
            """
            for page in reports['high_impressions_zero_clicks'][:10]:
                html += f"<tr><td>{page['page']}</td><td>{page['impressions']:,}</td><td>{page['position']:.1f}</td></tr>"
            html += "</table>"
        
        if reports.get('clicks_decreased_25pct'):
            html += """
                <h2>📉 صفحات با کاهش بیش از 25% در Clicks</h2>
                <table>
                    <tr><th>صفحه</th><th>Clicks قبلی</th><th>Clicks فعلی</th><th>تغییر</th></tr>
            """
            for page in reports['clicks_decreased_25pct'][:10]:
                change = page.get('clicks_change_percent', 0)
                html += f"<tr><td>{page['page']}</td><td>{page.get('previous_clicks', 0):,}</td><td>{page.get('current_clicks', 0):,}</td><td><span class='badge badge-negative'>{change:.1f}%</span></td></tr>"
            html += "</table>"
        
        if reports.get('highest_clicks'):
            html += """
                <h2>✅ صفحات با بیشترین Click</h2>
                <table>
                    <tr><th>صفحه</th><th>Clicks</th><th>Impressions</th><th>CTR</th></tr>
            """
            for page in reports['highest_clicks'][:10]:
                html += f"<tr><td>{page['page']}</td><td>{page['clicks']:,}</td><td>{page['impressions']:,}</td><td><span class='badge badge-positive'>{page['ctr']:.2f}%</span></td></tr>"
            html += "</table>"
        
        html += f"""
                <div class="footer">
                    <p>این ایمیل به صورت خودکار از SEO Analyze Pro ارسال شده است.</p>
                    <p>تاریخ ارسال: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_text_report(self, report_data: Dict[str, Any], property_name: str) -> str:
        """Create plain text email body"""
        period = report_data.get('period', 'Unknown')
        avg_position_change = report_data.get('avg_position_change', 0)
        
        text = f"""
گزارشات Google Search Console
==============================

Property: {property_name}
بازه زمانی: {period}

خلاصه گزارشات:
- تغییر میانگین Position: {avg_position_change:+.2f}
- دوره قبلی: {report_data.get('previous_period', 'N/A')}
- دوره فعلی: {report_data.get('current_period', 'N/A')}

برای مشاهده گزارشات کامل، لطفاً به پنل مدیریت مراجعه کنید.

---
این ایمیل به صورت خودکار از SEO Analyze Pro ارسال شده است.
تاریخ ارسال: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return text.strip()

