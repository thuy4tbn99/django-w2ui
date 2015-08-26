Django-W2UI demo project.

virtualenv test
cd test
. ./bin/activate
git clone https://github.com/ant9000/django-w2ui.git
cd django-w2ui/demoproject
pip install -r requirements.txt
./manage.py migrate
./manage.py loaddata sample_data
./manage.py runserver
