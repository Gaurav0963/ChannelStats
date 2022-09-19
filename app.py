from flask import Flask, render_template, request, session, send_file, redirect, url_for
from flask_cors import cross_origin
from pytube import YouTube
from youtubesearchpython import *
from pytube import Channel
import pafy
from io import BytesIO


app = Flask(__name__)
app.config['SECRET_KEY'] = "random012gibberish0458made2124things52easierfyugoldfjvbkduyfvahvkcsd"



@app.route('/', methods=['GET', 'POST'])  
@app.route('/home', methods=['GET', 'POST'])
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route("/about/")
@cross_origin()
def about():
    return render_template("about.html")



@app.route('/search/<int:start>/<int:end>/', methods=['POST','GET']) 
@cross_origin()
def index(start, end):
    #A check to stop from going back to welcome page if 'Page 1' button is clicked.
    if start == 1:
        app.logger.info("search button clicked from homepage")

        if request.method == 'POST':
            try:
                session['channel_url'] = request.form['search']

                reviews = FetchDataFromChannel_URL(start-1, end)

                return render_template('results.html', reviews=reviews[0:(len(reviews))])

            except Exception as e:
                app.logger.exception('Exception message from index func: ', e)
                return render_template('error.html')
        else:
            app.logger.warning("POST request failed on index function, returning to homepage")
            return render_template('index.html')
    else:
        app.logger.info("...using pagination...clicked on page_1 or page_2")
        reviews = FetchDataFromChannel_URL(start, end)
        return render_template('results.html', reviews=reviews[0:(len(reviews))])



def FetchDataFromChannel_URL(start,end):
    app.logger.info("Inside function FetchDataFromChannel_URL")
    
    video_tab = session['channel_url'] + "/videos"
    #importing session made it possible to copy and paste across functions

    channel = Channel(video_tab)

    video_url_list, results = [], []

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
        
        results.append(mydict)
    return results



@app.route('/download/<video_id>', methods=['POST', 'GET'])
@cross_origin()
def download_quality(video_id):

    app.logger.info("download button on results page has been clicked, videoID: ", video_id)
    
    link="https://www.youtube.com/watch?v="+video_id
    url = YouTube(link)
    return render_template('dnld.html', url=url)



@app.route('/download1/<video_id>', methods=['GET', 'POST'])
# @cross_origin
def download(video_id):
    if request.method=='POST':
        app.logger.info("POST request for downloading video is passed")
        buffer = BytesIO()

        link="https://www.youtube.com/watch?v="+video_id
        url = YouTube(link)
        itag = request.form.get('itag')
        video = url.streams.get_by_itag(itag)
        video.stream_to_buffer(buffer)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='video.mp4', mimetype='video/mp4')
    else:
        app.logger.warning("POST request did not went through for downloading video. function download(video_id)")
        return redirect(url_for('homePage'))



@app.route("/comments/<path:video_id>", methods=['GET', 'POST'])
@cross_origin()
def comment(video_id):
    comments = Comments(video_id)
    reviews = []

    while comments.hasMoreComments:
        comments.getNextComments()
        for i in range(len(comments.comments['result'])):
            name = comments.comments['result'][i]['author']['name']
            comnt = comments.comments['result'][i]['content']
            mydict = {'Name':name, 'Comment':comnt}
            reviews.append(mydict)
    return render_template('comment.html', reviews=reviews[0:(len(reviews))])



if __name__ == "__main__":
	app.run(port='1000',debug=True)