from flask import Flask, render_template, request
from flask_cors import cross_origin
from pytube import YouTube
from youtubesearchpython import *
from pytube import Channel
import pafy
import os


app = Flask(__name__)


def worker(start,end):
    with open("file.txt", "r") as f:
        text = f.readline()
        f.close
        channel = Channel(text)

        video_url_list, reviews = [], []

        for url in channel.video_urls[start:end]:
            
            video_url_list.append(url)

        for idx, video_url in enumerate(video_url_list):
            video = pafy.new(video_url)
            yt1 = YouTube(video_url)
            index = idx+start+1
            id = yt1.video_id
            name = video.author
            Title = video.title
            Likes = video.likes
            Views = video.viewcount
            Thumbnail = video.bigthumbhd

            mydict = {"index":index, "video_URL": video_url, "Title":Title , 'Likes':Likes, "Views": Views, "Thumbnail_link":Thumbnail, "id":id, "author":name}
            
            reviews.append(mydict)
        return reviews


@app.route('/', methods=['GET', 'POST'])  
@cross_origin()
def homePage():
    return render_template("new.html")


@app.route('/search/<int:start>/<int:end>/',methods=['POST','GET']) 
@cross_origin()
def index(start, end):
    if start == 1:
        if request.method == 'POST':
            try:
                channel_url = request.form['search']
                video_tab = channel_url + "/videos"
                with open("file.txt", "w") as file:
                    file.write(video_tab)
                    file.close
                reviews = worker(start-1, end)
                return render_template('results.html', reviews=reviews[0:(len(reviews))])
            except Exception as e:
                print('The Exception message is: ', e)
                return render_template('error.html')
        else:
            return render_template('new.html')
    else:
        reviews = worker(start, end)
        return render_template('results.html', reviews=reviews[0:(len(reviews))])


@app.route('/download/<text>', methods=['GET', 'POST'])
def download(text):
    download_Directory = 'C:\\YouTubeVideo\\Downloads'
    if not os.path.exists(download_Directory):
        os.makedirs(download_Directory)

    vdnld = pafy.new(text)
    filename = vdnld.title
    quality = vdnld.getbest()
    q = quality.get_filesize()
    try:
        # quality.download('D://')
        quality.download(download_Directory)
        return render_template("dnld.html", Filesize=(q//1024), filename=filename)
    except Exception as e:
        print(e)
        return 'DownloadError'


@app.route("/comments/<vid>", methods=['GET', 'POST'])
def comment(vid):
    comments = Comments(vid)
    reviews = []

    while comments.hasMoreComments:
        comments.getNextComments()
        for i in range(len(comments.comments['result'])):
            name = comments.comments['result'][i]['author']['name']
            comnt = comments.comments['result'][i]['content']
            mydict = {'Name':name, 'Comment':comnt}
            reviews.append(mydict)
    return render_template('comment.html', reviews=reviews[0:(len(reviews))])


@app.route("/about/")
def about():
    return render_template("about.html")



if __name__ == "__main__":
	app.run(port='5555',debug=True)