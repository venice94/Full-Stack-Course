#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, json
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database

db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

@app.route('/venues') # TO FIX: GROUP BY CITY/STATE AND SHOW >1 CITY/STATE
def venues():
  city_states = Venue.query.with_entities(Venue.city,Venue.state).distinct()
  for area in city_states:
    area_venue = Venue.query.filter(Venue.city==area.city,Venue.state==area.state)
    venue_show = area_venue.join(Show,Venue.id==Show.venue_id).with_entities(Venue.id,Venue.name,func.count(Show.id).label('num_upcoming_shows')).group_by(Venue.id,Venue.name).all()
    result = [{
      "city":area.city,
      "state":area.state,
      "venues": [{
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows":venue.num_upcoming_shows
      }]} for venue in venue_show]

    return render_template('pages/venues.html', areas=result)

@app.route('/venues/search', methods=['POST']) # Done
def search_venues():
  search_term=request.form['search_term']
  venues=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  count=len(venues)

  response={
    "count": count,
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>') # Done
def show_venue(venue_id):
  venue_info = Venue.query.get(venue_id)
  upcoming_shows = venue_info.shows.join(Artist,Artist.id==Show.artist_id).filter(Show.start_time>func.now()).with_entities(Show.artist_id,Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'),Show.start_time).all()
  past_shows = venue_info.shows.join(Artist,Artist.id==Show.artist_id).filter(Show.start_time<=func.now()).with_entities(Show.artist_id,Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'),Show.start_time).all()
  
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)

  result = {
    "id":venue_info.id,
    "name":venue_info.name,
    "city":venue_info.city,
    "state":venue_info.state,
    "address":venue_info.address,
    "phone":venue_info.phone,
    "genres":venue_info.genres,
    "image_link":venue_info.image_link,
    "facebook_link":venue_info.facebook_link,
    "website":venue_info.website,
    "seeking_talent":venue_info.seeking_talent,
    "seeking_description":venue_info.seeking_description,
    "upcoming_shows_count":upcoming_shows_count,
    "past_shows_count":past_shows_count,
    "upcoming_shows":upcoming_shows,
    "past_shows":past_shows
  }

  return render_template('pages/show_venue.html', venue=result)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET']) # Done
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST']) # TO FIX: Unable to add new venue
def create_venue_submission():
  name=request.form.get('name',"")
  city=request.form.get('city',"")
  state=request.form.get('state',"")
  address=request.form.get('address',"")
  phone=request.form.get('phone',"")
  genres=request.form.get('genres',"")
  image_link=request.form.get('image_link',"")
  facebook_link=request.form.get('facebook_link',"")
  website=request.form.get('website_link',"")
  seeking_talent=request.form.get('seeking_talent',True)
  seeking_description=request.form.get('seeking_description',"")

  error=False

  try:
    data = Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website=website,seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(data)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')    
  else:
    flash('Venue ' + data.name + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE']) # TO DO
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists') # Done
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST']) # Done
def search_artists():
  search_term=request.form['search_term']
  artists=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count=len(artists)

  response={
    "count": count,
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>') # Done
def show_artist(artist_id):
  artist_info = Artist.query.get(artist_id)

  if not artist_info:
    return render_template('errors/404.html')
  
  upcoming_shows = artist_info.shows.join(Venue,Venue.id==Show.venue_id).filter(Show.start_time>func.now()).with_entities(Show.venue_id,Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link'),Show.start_time).all()
  past_shows = artist_info.shows.join(Venue,Venue.id==Show.venue_id).filter(Show.start_time<=func.now()).with_entities(Show.venue_id,Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link'),Show.start_time).all()

  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  
  data={
    "id": artist_info.id,
    "name": artist_info.name,
    "genres": artist_info.genres,
    "city": artist_info.city,
    "state": artist_info.state,
    "phone": artist_info.phone,
    "website": artist_info.website,
    "facebook_link": artist_info.facebook_link,
    "seeking_venue": artist_info.seeking_venue,
    "seeking_description": artist_info.seeking_description,
    "image_link": artist_info.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET']) # Done
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist=Artist.query.get(artist_id)
  name=request.form.get('name',"")
  city=request.form.get('city',"")
  state=request.form.get('state',"")
  phone=request.form.get('phone',"")
  genres=request.form.get('genres',"")
  image_link=request.form.get('image_link',"")
  facebook_link=request.form.get('facebook_link',"")
  website=request.form.get('website_link',"")
  seeking_venue=request.form.get('seeking_venue',True)
  seeking_description=request.form.get('seeking_description',"")

  error=False

  try:
    artist.name=name
    artist.city=city
    artist.state=state
    artist.phone=phone
    artist.genres=genres
    artist.image_link=image_link
    artist.facebook_link=facebook_link
    artist.website=website
    artist.seeking_venue=seeking_venue
    artist.seeking_description=seeking_description
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    return render_template('errors/500.html')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

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
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
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
