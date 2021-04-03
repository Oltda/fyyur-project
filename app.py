#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#





class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    #artists = db.relationship('Artist', secondary=shows, backref=db.backref('venues', lazy=True))
    shows = db.relationship('Show', backref='venue', cascade="all, delete", lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))

    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)




    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #areas  returns this --> [('Prague', 'AZ'), ('Jihlava', 'DE')]

  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('state').all()

  prvni_filtr = Venue.query.filter_by(state=areas[0].state)
  #print(prvni_filtr)

  druhy_filtr = prvni_filtr.filter_by(city=areas[0].city).all()

  data = []
  for area in areas:
    venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).order_by('name').all()
    venue_data = []
    data.append({
      'city': area.city,
      'state': area.state,
      'venues': venue_data
    })
    for venue in venues:
      shows = Show.query.filter_by(venue_id=venue.id).order_by('id').all()
      venue_data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(shows)
      })

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"


  search_term = request.form.get('search_term', '')


  venue = db.session.query(Venue).order_by(Venue.name)

  response={
     "count": 1,
     "data": []
  }

  for i in venue:
    if search_term.lower() in i.name.lower():
      ven = {'name': i.name, 'id': i.id}
      response['data'].append((ven))
      #print(i.name)
  response['count'] = len(response['data'])



  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):



  venues = Venue.query.filter_by(id=venue_id).all()


  venue_info = venues[0]

  string_genres = "".join(venue_info.genres)
  string_genres = string_genres[1:-1]

  venue_info.genres = string_genres.split(",")




  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  return render_template('pages/show_venue.html', venue=venue_info)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    genres = request.form.getlist('genres')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    seeking_talent = request.form.get('seeking_talent', '')
    seeking_description = request.form.get('seeking_description', '')

    if seeking_talent == "y":
      seeking_talent = True
    else:
      seeking_talent = False



    venue = Venue(name=name, city=city, state=state, address=address,
                    phone=phone, image_link=image_link, genres=genres,
                    facebook_link=facebook_link, seeking_talent=seeking_talent,
                    seeking_description=seeking_description)



    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)

    db.session.delete(venue)
    db.session.commit()
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  return jsonify({'success': True})








  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage







#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()



  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  #{'count': 1, 'data': [{'name': 'U2', 'id': 39}]}

  search_term = request.form.get('search_term', '')


  artist = db.session.query(Artist).order_by(Artist.name)

  response={
     "count": 1,
     "data": []
  }

  for i in artist:
    if search_term.lower() in i.name.lower():
      arts = {'name': i.name, 'id': i.id}
      response['data'].append((arts))
      #print(i.name)
  response['count'] = len(response['data'])


  return render_template('pages/search_artists.html', results=response, search_term=search_term)





@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.filter_by(id=artist_id).first()




  string_genres = "".join(artist.genres)
  string_genres = string_genres[1:-1]

  artist.genres = string_genres.split(",")






  all_the_shows = Show.query.filter_by(artist_id=artist_id).all()

  past_shows = []
  upcoming_shows = []

  for gig in all_the_shows:

    # print("venue id", gig.venue_id)
    # print("venue image link", Venue.query.get(gig.venue_id).image_link)
    # print("venue name", Venue.query.get(gig.venue_id).name)


    show_date = gig.start_time
    today = datetime.datetime.now()

    if show_date.date() < today.date():
      info_past = {'venue_id': gig.venue_id, 'venue_name': Venue.query.get(gig.venue_id).name,
                   'venue_image_link': Venue.query.get(gig.venue_id).image_link,
                   'start_time': str(show_date)}
      past_shows.append(info_past)
      #print("show is in the past")
      #past_shows['venue_id'] = gig.venue_id
      # past_shows['venue_name'] = Venue.query.get(gig.venue_id).name
      # past_shows['venue_image_link'] = Venue.query.get(gig.venue_id).image_link
      # past_shows['start_time'] = str(show_date)
    elif show_date.date() > today.date():
      #print("the show is in the future")
      # upcoming_shows['venue_id'] = gig.venue_id
      # upcoming_shows['venue_name'] = Venue.query.get(gig.venue_id).name
      # upcoming_shows['venue_image_link'] = Venue.query.get(gig.venue_id).image_link
      # upcoming_shows['start_time'] = str(show_date)
      info_future = {'venue_id': gig.venue_id, 'venue_name': Venue.query.get(gig.venue_id).name,
                   'venue_image_link': Venue.query.get(gig.venue_id).image_link,
                   'start_time': str(show_date)}
      upcoming_shows.append(info_future)

    elif show_date.date() == today.date():
      print("the show is today")





  artist_data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "DODELAT column NENI V DATABAZI migrace",
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  print(artist_data)

  all_the_shows = Show.query.filter_by(artist_id=artist_id).all()

  # for gig in all_the_shows:
  #
  #   print("venue id", gig.venue_id)
  #   print("venue image link", Venue.query.get(gig.venue_id).image_link)
  #   print("venue name", Venue.query.get(gig.venue_id).name)
  #
  #   print("start time", gig.start_time)
  #   show_date = gig.start_time
  #
  #   x = datetime.datetime.now()
  #
  #   if show_date.date() < x.date():
  #     print("show is in the past")
  #   elif show_date.date() > x.date():
  #     print("the show is in the future")
  #   elif show_date.date() == x.date():
  #     print("the show is today")

  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }

  dataa = {'id': 39,
           'name': 'U2',
           'genres': ['Blues', 'Country', 'Electronic'],
           'city': 'Idaho',
           'state': 'AZ',
           'phone': '12345',
           'website': 'DODELAT column NENI V DATABAZI migrace',
           'facebook_link': 'dalsi fb',
           'seeking_venue': True,
           'seeking_description': 'Ireland music',
           'image_link': 'dasli image',
           'past_shows': [
                          {'venue_id': 38,
                           'venue_name': 'Accustic bar',
                           'venue_image_link': 'acust image',
                            'start_time': '2021-04-02 13:30:04'},

                          {'venue_id': 35, ''
                            'venue_name': 'novej ',
                            'venue_image_link': 'novej img',
                            'start_time': '2021-04-01 14:10:13'}],

           'upcoming_shows': [
                              {'venue_id': 37,
                               'venue_name': 'German bar',
                               'venue_image_link': 'germ img', 'start_time': '2021-04-04 11:50:20'}],
           'past_shows_count': 1, 'upcoming_shows_count': 0}



  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_to_edit = Artist.query.filter_by(id=artist_id).first()

  form.name.data = artist_to_edit.name
  form.city.data = artist_to_edit.city
  form.state.data = artist_to_edit.state
  form.phone.data = artist_to_edit.phone
  form.image_link.data = artist_to_edit.image_link
  form.facebook_link.data = artist_to_edit.facebook_link

  form.seeking_description.data = artist_to_edit.seeking_description

  form.seeking_venue.data = artist_to_edit.seeking_venue





  string_genres = "".join(artist_to_edit.genres)
  string_genres = string_genres[1:-1]

  artist_to_edit.genres = string_genres.split(",")


  # for genre in artist_to_edit.genres:
  #    form.genres.data = genre

  form.genres.data = artist_to_edit.genres






  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_to_edit)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_to_edit = Artist.query.filter_by(id=artist_id).first()

  name = request.form.get('name', '')

  city = request.form.get('city', '')
  state = request.form.get('state', '')
  phone = request.form.get('phone', '')

  genres = request.form.getlist('genres')
  image_link = request.form.get('image_link', '')
  facebook_link = request.form.get('facebook_link', '')
  seeking_venue = request.form.get('seeking_venue', '')
  seeking_description = request.form.get('seeking_description', '')


  if seeking_venue == "y":
      artist_to_edit.seeking_venue = True
  else:
      artist_to_edit.seeking_venue = False


  artist_to_edit.name = name
  artist_to_edit.city = city
  artist_to_edit.state = state
  artist_to_edit.phone = phone
  artist_to_edit.genres = genres
  artist_to_edit.image_link = image_link
  artist_to_edit.facebook_link = facebook_link
  artist_to_edit.seeking_description = seeking_description


  db.session.commit()
  db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue_to_edit = Venue.query.get(venue_id)

  form.name.data = venue_to_edit.name
  form.city.data = venue_to_edit.city
  form.state.data = venue_to_edit.state
  form.phone.data = venue_to_edit.phone
  form.address.data = venue_to_edit.address
  form.image_link.data = venue_to_edit.image_link
  form.facebook_link.data = venue_to_edit.facebook_link

  form.seeking_description.data = venue_to_edit.seeking_description

  form.seeking_talent.data = venue_to_edit.seeking_talent





  string_genres = "".join(venue_to_edit.genres)
  string_genres = string_genres[1:-1]

  venue_to_edit.genres = string_genres.split(",")


  # for genre in artist_to_edit.genres:
  #    form.genres.data = genre

  form.genres.data = venue_to_edit.genres


  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_to_edit)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue_to_edit = Venue.query.get(venue_id)

  name = request.form.get('name', '')

  city = request.form.get('city', '')
  state = request.form.get('state', '')
  phone = request.form.get('phone', '')

  address = request.form.get('address', '')
  genres = request.form.getlist('genres')
  image_link = request.form.get('image_link', '')
  facebook_link = request.form.get('facebook_link', '')
  seeking_talent = request.form.get('seeking_talent', '')
  seeking_description = request.form.get('seeking_description', '')

  if seeking_talent == "y":
    venue_to_edit.seeking_talent = True
  else:
    venue_to_edit.seeking_talent = False

  venue_to_edit.name = name
  venue_to_edit.city = city
  venue_to_edit.state = state
  venue_to_edit.phone = phone
  venue_to_edit.genres = genres
  venue_to_edit.image_link = image_link
  venue_to_edit.city = facebook_link
  venue_to_edit.phone = seeking_description
  venue_to_edit.address = address

  db.session.commit()
  db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name', '')
  city = request.form.get('city', '')
  state = request.form.get('state', '')
  phone = request.form.get('phone', '')

  genres = request.form.getlist('genres')
  image_link = request.form.get('image_link', '')
  facebook_link = request.form.get('facebook_link', '')
  seeking_venue = request.form.get('seeking_venue', '')
  seeking_description = request.form.get('seeking_description', '')



  if seeking_venue == "y":
    seeking_venue = True
  else:
    seeking_venue = False


  artist = Artist(name=name, city=city, state=state,
                  phone=phone, genres=genres, image_link=image_link,
                  facebook_link=facebook_link,
                  seeking_description=seeking_description, seeking_venue=seeking_venue)
  db.session.add(artist)
  db.session.commit()
  db.session.close()

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  all_shows = Show.query.all()


  show_data = []
  for show in all_shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist = Artist.query.filter_by(id=show.artist_id).first()
    show_data.append({
    "venue_id": show.venue_id,
    "venue_name": venue.name,
    "artist_id": show.artist_id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form.get('artist_id', '')
  venue_id = request.form.get('venue_id', '')
  start_time = request.form.get('start_time', '')



  show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

  db.session.add(show)

  db.session.commit()
  db.session.close()



   # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
