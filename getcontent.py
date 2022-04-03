import sqlite3

db = sqlite3.connect("users.db", check_same_thread=False)
cur = db.cursor()

blog = """<div class="content-cont">
            <div class="content">
                <h1>Title</h1>
                <h4><a href="/u/user">user</a></h4>
                <p>contents</p>
                <h4 style="text-align: right;">datetime</h4>
            </div>
        </div>"""

twitter = """\n<blockquote class="twitter-tweet">
            <a href="url"></a>
        </blockquote>\n"""

youtube = """<iframe width=100% height="315" src="https://www.youtube.com/embed/videoid" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""


def get_cont_all():
    content = ""
    cur.execute("select * from blog")
    data = cur.fetchall()
    data.reverse()

    for entry in data:
        if entry[2] == 0:
            cur.execute(f"select username from users where userid={entry[1]}")
            username = cur.fetchall()[0][0]
            cc = blog.replace("contents", entry[4])
            cc = cc.replace("user", username)
            cc = cc.replace("datetime", entry[5])
            content += (cc.replace("Title", entry[3]))
        elif entry[2] == 1:
            content += (twitter.replace("url", entry[4]))
        elif entry[2] == 2:
            content += (youtube.replace("videoid", entry[4]))
    return(content)


def get_cont_user(userid):
    content = ""
    cur.execute(f"select * from blog where userid={userid}")
    data = cur.fetchall()
    data.reverse()

    for entry in data:
        if entry[2] == 0:
            cur.execute(f"select username from users where userid={entry[1]}")
            username = cur.fetchall()[0][0]
            cc = blog.replace("contents", entry[4])
            cc = cc.replace("user", username)
            cc = cc.replace("datetime", entry[5])
            content += (cc.replace("Title", entry[3]))
        elif entry[2] == 1:
            content += (twitter.replace("url", entry[4]))
        elif entry[2] == 2:
            content += (youtube.replace("videoid", entry[4]))
    return(content)
