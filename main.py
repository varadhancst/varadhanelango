import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from datetime import date, datetime
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
import smtplib
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from forms import LoginForm, RegisterForm, CommentForm, CreateProjectForm, ResumeForm
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path="/static/")

OWN_EMAIL = os.getenv('OWN_EMAIL')
OWN_PASSWORD = os.getenv('OWN_PASSWORD')
FILTER_OPTIONS = ["Scripting", "Web Development", "GUI", "Game", "Desktop", "HTTP Requests & APIs",
                  "Image Processing & Data Science", "Web Scraping", "Automation", "Data Science"]
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
ckeditor = CKEditor(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("Project", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    img_1 = db.Column(db.String(250), nullable=False)
    img_2 = db.Column(db.String(250), nullable=False)
    img_3 = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)
    proj_cate = db.Column(db.String(250), nullable=False)
    client = db.Column(db.String(250), nullable=False)
    proj_url = db.Column(db.String(250), nullable=False)
    proj_video = db.Column(db.String(250), nullable=False)
    technologies = db.Column(db.String(250), nullable=False)
    tools = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")

    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary

    def __repr__(self):
        return f'<Project {self.name}>'


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("Project", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_url = db.Column(db.String(250), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)


db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=form.email.data, name=form.name.data, password=hash_and_salted_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home_page"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home_page'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/', methods=['POST', 'GET'])
def home_page():
    # posts = Project.query.all()
    posts = db.session.query(Project).order_by(Project.priority.asc()).all()
    resumes = db.session.query(Resume).order_by(Resume.id.desc()).limit(1).all()
    birth_date = "22 May 1990"
    birthday = (date(1990, 5, 22))
    send_msg = None

    def calculateAge(birthDate):
        today = date.today()
        age_year = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
        return age_year

    age = calculateAge(birthday)

    if request.method == 'POST':
        data = request.form
        send_email(data["name"], data["email"], data["subject"], data["message"])
        send_msg = "msg sent successfully"
        flash("msg sent successfully")
        return send_msg

    return render_template("index.html", birth_date=birth_date, all_posts=posts, all_resumes=resumes, age=age,
                           mes_sent=send_msg, current_user=current_user, filter_options=FILTER_OPTIONS,
                           length=len(FILTER_OPTIONS))


@app.route("/new-resume", methods=["GET", "POST"])
@admin_only
def resume():
    resume_form = ResumeForm()
    if resume_form.validate_on_submit():
        new_resume = Resume(resume_url=resume_form.cv_URL.data, date=datetime.now())
        db.session.add(new_resume)
        db.session.commit()
        return redirect(url_for("home_page"))

    return render_template("resume.html", form=resume_form, current_user=current_user)


@app.get("/projects/project")
# @app.get("/")
def get_specific_projects():
    query_param = request.args.get("q")
    all_projects = [project_name.to_dict() for project_name in Project.query.all()]
    results = []

    for project_name in all_projects:
        if project_name["proj_cate"] == query_param:
            results.append(project_name)

    return render_template("index.html", results=results)


@app.route("/portfolio-details/<int:post_id>", methods=["GET", "POST"])
def portfolio(post_id):
    form = CommentForm()
    requested_post = Project.query.get(post_id)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(text=form.comment_text.data, comment_author=current_user, parent_post=requested_post)
        db.session.add(new_comment)
        db.session.commit()

    return render_template("portfolio-details.html", post=requested_post, form=form, current_user=current_user)


@app.route("/new-project", methods=["GET", "POST"])
@admin_only
def add_new_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        new_project = Project(priority=form.priority.data, title=form.title.data, subtitle=form.subtitle.data,
                              img_1=form.img_1.data, img_2=form.img_2.data, img_3=form.img_3.data,
                              description=form.description.data, proj_cate=form.proj_cate.data, client=form.client.data,
                              proj_url=form.proj_url.data, proj_video=form.proj_video.data,
                              technologies=form.technologies.data, tools=form.tools.data, author=current_user,
                              date=date.today().strftime("%B %d, %Y"))
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("home_page", _anchor='project'))

    return render_template("make-project.html", form=form, current_user=current_user)


@app.route("/edit-project/<int:project_id>", methods=["GET", "POST"])
@admin_only
def edit_project(project_id):
    post = Project.query.get(project_id)
    edit_form = CreateProjectForm(priority=post.priority, title=post.title, subtitle=post.subtitle, img_1=post.img_1,
                                  img_2=post.img_2, img_3=post.img_3, description=post.description,
                                  proj_cate=post.proj_cate, client=post.client, proj_url=post.proj_url,
                                  proj_video=post.proj_video, technologies=post.technologies, tools=post.tools,
                                  author=current_user, )
    if edit_form.validate_on_submit():
        post.priority = edit_form.priority.data
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_1 = edit_form.img_1.data
        post.img_2 = edit_form.img_2.data
        post.img_3 = edit_form.img_3.data
        post.description = edit_form.description.data
        post.proj_cate = edit_form.proj_cate.data
        post.client = edit_form.client.data
        post.proj_url = edit_form.proj_url.data
        post.proj_video = edit_form.proj_video.data
        post.technologies = edit_form.technologies.data
        post.tools = edit_form.tools.data
        db.session.commit()
        return redirect(url_for("portfolio", post_id=post.id))

    return render_template("make-project.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:project_id>", methods=["GET", "POST"])
@admin_only
def delete_project(project_id):
    project_to_delete = Project.query.get(project_id)
    db.session.delete(project_to_delete)
    db.session.commit()
    return redirect(url_for('home_page', _anchor='project'))


def send_email(name, mail, tel, message):
    email_message = f"Subject:Message from portfolio website\n\nName: {name}\nEmail: {mail}\nSubject: {tel}\nMessage:{message} "
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True)
