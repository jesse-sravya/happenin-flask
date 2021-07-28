# happenin-flask


To run app locally:


1. Clone the repo and cd into it
```
cd happenin-flask
```
2. Create a `.flaskenv` file with the following key value pairs
```
FLASK_APP=app.py
FLASK_ENV=development

GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
GOOGLE_CALENDAR_ID=<YOUR_GOOGLE_CALENDAR_ID>
```
3. Create a venv and activate it
```
python python3 -m venv venv
source venv/bin/activate
```
4. Install requirements
```
pip3 install -r requirements.txt
```
5. Run the flask server
```
flask shell
```


The app should be up and running on http://localhost:5000/
