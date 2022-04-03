from datetime import datetime
from urllib.parse import urlparse, parse_qs
from flask import *
import getcontent
import sqlite3
import re

db = sqlite3.connect("users.db", check_same_thread=False)
cur = db.cursor()


def getuser():
    userid = request.cookies.get("user")
    if userid:
        cur.execute(f"select username from users where userid={userid}")
        username = cur.fetchall()[0][0]
        return username
    else:
        return ""


def getdatetime():
    now = datetime.now()
    date_time = now.strftime("-%H:%M:%S -%d/%m/%Y")
    return date_time


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    return False


def usercheck(username):
    li = []
    cur.execute("SELECT username FROM users ;")
    li = cur.fetchall()
    if(username in li):
        return True
    return False


def get_yt_id(url, ignore_playlist=True):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/':
            return query.path.split('/')[1]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html", allcontents=Markup(getcontent.get_cont_all()), username=getuser())


@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html", username=getuser())


@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = str(hash(request.form['password']))[7]
    cur.execute(f"select password from users where email='{email}'")
    try:
        pass1 = cur.fetchall()[0][0]
    except:
        return redirect('/login')
    if(password != pass1):
        return redirect("/login")
    cur.execute(f"select userid from users where email='{email}'")
    userid = cur.fetchall()[0][0]
    res = redirect('/')
    res.set_cookie("user", value=str(userid))
    return res


@app.route('/register')
def register():
    return render_template("register.html", username=getuser())


@app.route('/register', methods=['POST'])
def register_post():
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    if(check(email) == False):
        redirect("/register")
    username = request.form['username']
    if(usercheck(username) == True):
        redirect("/register")
    password = str(hash(request.form['password']))[7]
    cur.execute("select max(userid) from users")
    userid = cur.fetchall()[0][0] + 1
    cur.execute(
        f"insert into users (userid,first_name,last_name,email,password,username) values ({userid}, '{fname}', '{lname}','{email}','{password}','{username}')")
    db.commit()
    return redirect('/')


@app.route('/edit')
def edit():
    return render_template("edit.html", username=getuser())


@app.route('/edit', methods=['POST'])
def editprofle():
    twitter = request.form['twitter']
    youtube = request.form['youtube']
    userid = request.cookies.get('user')

    if twitter:
        cur.execute(
            f"UPDATE USERS SET twitter = '{twitter}' where userid={userid}")

    if youtube:
        cur.execute(
            f"UPDATE USERS SET youtube = '{youtube}' where userid={userid}")
    db.commit()
    return redirect('/')


@app.route('/addblog')
def addblog():
    if request.cookies.get('user'):
        return render_template("add_blog.html", username=getuser())
    else:
        return redirect('login')


@app.route('/addblog', methods=['POST'])
def addblog_post():
    title = request.form['title']
    content = request.form['blog']
    userid = request.cookies.get('user')
    cur.execute("select max(blogid) from blog")
    blogid = cur.fetchall()[0][0] + 1
    date_time = getdatetime()
    cur.execute(
        f"insert into blog (blogid,userid, type,title,content,datetime) values ({blogid}, {userid}, 0, '{title}','{content}','{date_time}')")
    db.commit()
    return redirect('/')


@app.route('/addtweet')
def addtweet():
    if request.cookies.get('user'):
        return render_template('addtweet.html', username=getuser())
    else:
        return redirect('login')


@app.route('/addtweet', methods=['POST'])
def addtwat():
    tweeturl = request.form.get('tweeturl')
    userid = request.cookies.get('user')
    cur.execute("select max(blogid) from blog")
    blogid = cur.fetchall()[0][0] + 1
    date_time = getdatetime()
    cur.execute(
        f"insert into blog (blogid, userid, type, content, datetime) values ({blogid}, {userid}, 1, '{tweeturl}', '{date_time}')")
    db.commit()
    return redirect('/')


@app.route('/addvideo')
def addvideo():
    if request.cookies.get('user'):
        return render_template('addvideo.html', username=getuser())
    else:
        return redirect('login')


@app.route('/addvideo', methods=['POST'])
def addvid():
    videourl = get_yt_id(request.form.get('videourl'))
    if videourl:
        userid = request.cookies.get('user')
        cur.execute("select max(blogid) from blog")
        blogid = cur.fetchall()[0][0] + 1
        date_time = getdatetime()
        cur.execute(
            f"insert into blog (blogid, userid, type, content, datetime) values ({blogid}, {userid}, 2, '{videourl}', '{date_time}')")
        db.commit()
    return redirect('/')


@app.route('/logout')
def logout():
    res = redirect('/')
    res.set_cookie('user', '', expires=0)
    return res


@app.route('/u/<user>')
def userpage(user):
    cur.execute(f"select userid from users where username='{user}'")
    id = cur.fetchall()[0][0]
    cur.execute(f"select first_name from users where username='{user}'")
    fname = cur.fetchall()[0][0]
    if id:
        return render_template('blog.html', firstname=fname, allcontents=Markup(getcontent.get_cont_user(id)), username=getuser())
    else:
        return "404 error"


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
