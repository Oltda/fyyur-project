#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('state').all()

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

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

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

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))





@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):


  venue = Venue.query.filter_by(id=venue_id).first()
  all_the_shows = Show.query.filter_by(venue_id=venue_id).all()

  past_shows = []
  upcoming_shows = []

  for gig in all_the_shows:

    show_date = gig.start_time
    today = datetime.datetime.now()

    if show_date.date() < today.date():
      info_past = {'artist_id': gig.artist_id, 'artist_name': Artist.query.get(gig.artist_id).name,
                   'artist_image_link': Artist.query.get(gig.artist_id).image_link,
                   'start_time': str(show_date)}
      past_shows.append(info_past)

    elif show_date.date() >= today.date():
      info_future = {'artist_id': gig.artist_id, 'artist_name': Artist.query.get(gig.artist_id).name,
                   'artist_image_link': Artist.query.get(gig.artist_id).image_link,
                   'start_time': str(show_date)}
      upcoming_shows.append(info_future)


  venue_data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }


  # TODO: replace with real venue data from the venues table, using venue_id
  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():


  try:

    seeking_talent = request.form.get('seeking_talent', '')
    if seeking_talent == "y":
      seeking_talent = True
    else:
      seeking_talent = False

    venue = Venue(
          name =request.form.get('name', ''),
          city=request.form.get('city', ''),
          state = request.form.get('state', ''),
          genres = request.form.getlist('genres'),
          address=request.form.get('address', ''),
          phone=request.form.get('phone', ''),
          image_link=request.form.get('image_link', ''),
          facebook_link=request.form.get('facebook_link', ''),
          seeking_talent=seeking_talent,
          seeking_description=request.form.get('seeking_description', ''),
          website_link=request.form.get('website_link', '')
    )

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
  if error:
    flash("There was a problem deleting the venue")
  else:
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
  response['count'] = len(response['data'])


  return render_template('pages/search_artists.html', results=response, search_term=search_term)





@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.filter_by(id=artist_id).first()

  all_the_shows = Show.query.filter_by(artist_id=artist_id).all()

  past_shows = []
  upcoming_shows = []

  for gig in all_the_shows:
    show_date = gig.start_time
    today = datetime.datetime.now()

    if show_date.date() < today.date():
      info_past = {'venue_id': gig.venue_id, 'venue_name': Venue.query.get(gig.venue_id).name,
                   'venue_image_link': Venue.query.get(gig.venue_id).image_link,
                   'start_time': str(show_date)}
      past_shows.append(info_past)

    elif show_date.date() >= today.date():

      info_future = {'venue_id': gig.venue_id, 'venue_name': Venue.query.get(gig.venue_id).name,
                   'venue_image_link': Venue.query.get(gig.venue_id).image_link,
                   'start_time': str(show_date)}
      upcoming_shows.append(info_future)



  artist_data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

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
  form.website_link.data = artist_to_edit.website_link
  form.seeking_description.data = artist_to_edit.seeking_description
  form.seeking_venue.data = artist_to_edit.seeking_venue
  form.genres.data = artist_to_edit.genres

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_to_edit)




@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  artist_to_edit = Artist.query.filter_by(id=artist_id).first()

  try:
    seeking_venue = request.form.get('seeking_venue', '')

    artist_to_edit.name = request.form.get('name', '')
    artist_to_edit.city = request.form.get('city', '')
    artist_to_edit.state = request.form.get('state', '')
    artist_to_edit.phone = request.form.get('phone', '')
    artist_to_edit.genres = request.form.getlist('genres')
    artist_to_edit.image_link = request.form.get('image_link', '')
    artist_to_edit.facebook_link = request.form.get('facebook_link', '')
    artist_to_edit.seeking_description = request.form.get('seeking_description', '')
    artist_to_edit.website_link = request.form.get('website_link', '')
    if seeking_venue == "y":
        artist_to_edit.seeking_venue = True
    else:
        artist_to_edit.seeking_venue = False

    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully edited!')
  except:
    flash('There was an error. Artist ' + form.name.data + ' could not be edited')
    db.session.rollback()
  finally:
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
  form.website_link.data = venue_to_edit.website_link
  form.seeking_description.data = venue_to_edit.seeking_description
  form.seeking_talent.data = venue_to_edit.seeking_talent
  form.genres.data = venue_to_edit.genres


  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_to_edit)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue_to_edit = Venue.query.get(venue_id)

  try:
    seeking_talent = request.form.get('seeking_talent', '')
    if seeking_talent == "y":
      venue_to_edit.seeking_talent = True
    else:
      venue_to_edit.seeking_talent = False

    venue_to_edit.name = request.form.get('name', '')
    venue_to_edit.city = request.form.get('city', '')
    venue_to_edit.state = request.form.get('state', '')
    venue_to_edit.phone = request.form.get('phone', '')
    venue_to_edit.genres = request.form.getlist('genres')
    venue_to_edit.image_link = request.form.get('image_link', '')
    venue_to_edit.facebook_link = request.form.get('facebook_link', '')
    venue_to_edit.seeking_description = request.form.get('seeking_description', '')
    venue_to_edit.address = request.form.get('address', '')
    venue_to_edit.website_link = request.form.get('website_link', '')

    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully edited!')
  except:
    flash('There was an error. Venue ' + form.name.data + ' could not be edited')
    db.session.rollback()
  finally:
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

  try:
    seeking_venue = request.form.get('seeking_venue', '')

    if seeking_venue == "y":
      seeking_venue = True
    else:
      seeking_venue = False

    artist = Artist(
              name=request.form.get('name', ''),
              city=request.form.get('city', ''),
              state=request.form.get('state', ''),
              phone=request.form.get('phone', ''),
              genres=request.form.getlist('genres'),
              image_link=request.form.get('image_link', ''),
              facebook_link=request.form.get('facebook_link', ''),
              website_link=request.form.get('website_link', ''),
              seeking_description=request.form.get('seeking_description', ''),
              seeking_venue=seeking_venue
    )


    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')



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

  try:
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    db.session.add(show)
    db.session.commit()
    flash('Your show has been successfully listed.')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')



   # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


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



from models import Venue, Artist, Show


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
