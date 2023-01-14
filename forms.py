from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, FileField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class CreateProjectForm(FlaskForm):
    priority = IntegerField("Priority No", validators=[DataRequired()])
    title = StringField("Project Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_1 = StringField("Img_1 URL", validators=[DataRequired(), URL()])
    img_2 = StringField("Img_2 URL", validators=[DataRequired(), URL()])
    img_3 = StringField("Img_3 URL", validators=[DataRequired(), URL()])
    description = CKEditorField("Project Description", validators=[DataRequired()])
    proj_cate = SelectField("Category", validators=[DataRequired()], choices=(
        "Scripting", "Web Development", "GUI", "Game", "Desktop", "HTTP Requests & APIs",
        "Image Processing & Data Science",
        "Web Scraping", "Automation", "Data Science"))
    client = StringField("Client", validators=[DataRequired()])
    proj_url = StringField("Project URL", validators=[DataRequired(), URL()])
    proj_video = StringField("Project Video URL", validators=[DataRequired(), URL()])
    technologies = StringField("technologies", validators=[DataRequired()])
    tools = StringField("tools", validators=[DataRequired()])
    submit = SubmitField("Submit Project")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class ResumeForm(FlaskForm):
    cv_URL = StringField("Resume URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Upload Profile")
