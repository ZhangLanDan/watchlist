from flask import Flask,render_template,url_for,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)

@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database')

@app.cli.command()
def forge():
    db.create_all()

    name = "Lili"
    movies = [{'title': 'My Neighbor Totoro', 'year': '1988'},
{'title': 'Dead Poets Society', 'year': '1989'},
{'title': 'A Perfect World', 'year': '1993'},
{'title': 'Leon', 'year': '1994'},
{'title': 'Mahjong', 'year': '1996'},
{'title': 'Swallowtail Butterfly', 'year': '1996'},
{'title': 'King of Comedy', 'year': '1999'},
{'title': 'Devils on the Doorstep', 'year': '1999'},
{'title': 'WALL-E', 'year': '2008'},
{'title': 'The Pork of Music', 'year': '2012'},
]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')


class User(db.Model):
    id_ = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id_ = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid Input')
            return redirect(url_for('index'))

        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',user=user,movies=movies)

@app.route('/user/<name>')
def user_page(name):
    return f"User: {name}"

@app.route('/test')
def test_url_for():
    print(url_for('index'))
    print(url_for('user_page',name='Kii'))
    print(url_for('user_page',name='Lili'))
    print(url_for('test_url_for',num=2))
    return 'Test Page'

@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year)>4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title # 更新标题
        movie.year = year # 更新年份
        db.session.commit() # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index')) # 重定向回主页
    return render_template('edit.html', movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html')

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

