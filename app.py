from flask import Flask, request, render_template_string, redirect, url_for
import requests
from requests.auth import HTTPBasicAuth
import os

flask_app = Flask(__name__)

API_URL = "https://sandbox.api.sap.com/successfactors/odata/v2/PerPhone"
PERSONAL_INFO_URL = "https://sandbox.api.sap.com/successfactors/odata/v2/PerPersonal"
JOB_INFO_URL = "https://sandbox.api.sap.com/successfactors/odata/v2/EmpJob"
COMP_INFO_URL = "https://sandbox.api.sap.com/successfactors/odata/v2/Compensation"

USERNAME = "sfapi@SFCPART000716"
PASSWORD = "Welcome@12345"

HTML_FORM = """
    <h2>Employee Self Service</h2>
    <form method="POST">
        <label for="mobile">Enter Mobile Number:</label><br>
        <input type="text" id="mobile" name="mobile" required><br><br>
        <input type="submit" value="Validate">
    </form>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
"""

MENU_PAGE = """
    <h2>Welcome {{ person_id }}</h2>
    <ul>
        <li><a href="/personal/{{ person_id }}">View personal information</a></li>
        <li><a href="/job/{{ person_id }}">View job information</a></li>
        <li><a href="/comp/{{ person_id }}">View compensation information</a></li>
    </ul>
"""

INFO_PAGE = """
    <h2>{{ title }}</h2>
    <pre>{{ info }}</pre>
    <a href="/">Back to Home</a>
"""

@flask_app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mobile = request.form['mobile']
        headers = {
            "Accept": "application/json",
            "APIKey": API_KEY
        }
        params = {
            "$filter": f"phoneNumber eq '{mobile}' and phoneType eq '10605'"
        }
        response = requests.get(API_URL, headers=headers, params=params, auth=HTTPBasicAuth(USERNAME, PASSWORD))

        if response.status_code == 200:
            data = response.json()
            results = data.get('d', {}).get('results', [])
            if results:
                person_id = results[0].get('personIdExternal')
                return render_template_string(MENU_PAGE, person_id=person_id)
            else:
                return render_template_string(HTML_FORM, error="Phone number cannot be found. Contact your HR.")
        else:
            return render_template_string(HTML_FORM, error="API connection failed.")

    return render_template_string(HTML_FORM, error=None)

@flask_app.route('/personal/<person_id>')
def personal_info(person_id):
    return fetch_info(PERSONAL_INFO_URL, person_id, "Personal Information")

@flask_app.route('/job/<person_id>')
def job_info(person_id):
    return fetch_info(JOB_INFO_URL, person_id, "Job Information")

@flask_app.route('/comp/<person_id>')
def compensation_info(person_id):
    return fetch_info(COMP_INFO_URL, person_id, "Compensation Information")

def fetch_info(url, person_id, title):
    headers = {
        "Accept": "application/json",
        "APIKey": API_KEY
    }
    params = {
        "$filter": f"personIdExternal eq '{person_id}'"
    }
    response = requests.get(url, headers=headers, params=params, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        data = response.json()
        return render_template_string(INFO_PAGE, info=data, title=title)
    else:
        return render_template_string(INFO_PAGE, info=f"Failed to fetch {title.lower()}.", title=title)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(debug=True, host="0.0.0.0", port=port)
