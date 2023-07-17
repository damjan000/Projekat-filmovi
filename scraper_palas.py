from flask import Flask
from bs4 import BeautifulSoup
from flask_mysqldb import MySQL
import yaml
import requests


app=Flask(__name__)
with open('db.yaml','r') as file:
    db=yaml.safe_load(file)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql=MySQL(app)
baza=0
with app.app_context():
    cur=mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM Movies")
    baza=cur.fetchone()[0]

class scraper():

    if baza==0:
        base_url='https://www.cineplexxpalas.ba/movies/'
        current_page=900

        while current_page<=1070:
            url=base_url+str(current_page)
            palas_req=requests.get(url)
            palas_req_soup=BeautifulSoup(palas_req.text, 'html.parser')
            palas_req_soup.prettify
            
            try:
                content=str(palas_req_soup.find_all('div', {'class' : 'movie-details-text'}))
                content=content.replace('</p>\n','')
                content=content.replace('</p> </div>','')
                content=content.replace('<br/>','')
                content=content.split('<p>')
                content.remove(content[0])
                time=0
                actor=''
                genre=''
                desciptrion=''
                title=palas_req_soup.find('h1',{'class':'movie-title'}).string
                url_img=palas_req_soup.find('div',{'class':'item-img'})
                url_img=url_img.find('img').get('src')
                
                for i in content:
                    i=i.removesuffix(']')
                    if i.startswith('Uloge:')  or i.startswith('Glavne uloge:') or i.startswith('Glumci:'):
                        actor=i.removeprefix('Uloge:')
                        actor=actor.removeprefix('Glavne uloge:')
                        actor=actor.removeprefix('Glumci:')
                        actor=actor.replace('<a>','')
                        actor=actor.replace('</a>','')
                        actor=actor.replace('ali i mlade snage','')
                        actor=actor.removeprefix(' ')
                        actor=actor.removesuffix(' ') 
                        actor=actor.split(',')
                        for i in actor:
                            if i.find(' with ')>0:
                                j=i.split(' with ')
                                actor.append(j[0])
                                actor.append(j[1])
                                actor.remove(i)
                            elif i.find(' i ')>0:
                                j=i.split(' i ')
                                actor.append(j[0])
                                actor.append(j[1])
                                actor.remove(i)
                    elif i.startswith('Trajanje'):
                        time=i.removeprefix('Trajanje filma: ')
                        time=time.removeprefix('Trajanje: ')
                        time=time.removesuffix('min.')
                        time=time.removesuffix(' min')
                    elif i.startswith('Žanr: '):
                        genre=i.removeprefix('Žanr: ')
                    elif i.startswith('Rež')==False:
                        if i.startswith('Glav')==False:
                            if i.startswith('Orig')==False:
                                if i.startswith('Ulog')==False:
                                    desciptrion=desciptrion+i
                                    
                if genre=='' or desciptrion=='' or time==0 or actor=='':
                    genre=''
                else:
                    with app.app_context():
                        cur = mysql.connection.cursor()
                        cur.execute("INSERT IGNORE INTO movies(title,duration,genre,description,image_url) VALUES (%s,%s,%s,%s,%s)",
                                    [title, time, genre, desciptrion,url_img])
                        movie_id=cur.lastrowid
                        for i in actor:
                            cur.execute("INSERT IGNORE INTO actors(full_name,movie_id) VALUES (%s,%s)", [i,movie_id])
                        mysql.connection.commit() 
                        cur.close()  
            except Exception as e:
                print(e)
            current_page=current_page+1
