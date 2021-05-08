#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, json, abort
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

@app.route('/venues') # Done
def venues():
  city_states = Venue.query.with_entities(Venue.city,Venue.state).distinct().all()
  result=[]
  for area in city_states:
      area_venue = Venue.query.filter(Venue.city==area.city,Venue.state==area.state)
      venue_show = area_venue.join(Show,Venue.id==Show.venue_id, isouter=True).with_entities(Venue.id,Venue.name,func.count(Show.id).label('num_upcoming_shows')).group_by(Venue.id,Venue.name).all()
      venues = []
      for venue in venue_show:
          venues.append({
            'id':venue.id,
            'name':venue.name,
            'num_upcoming_shows':venue.num_upcoming_shows
          })
      result.append({
        'city':area.city,
        'state':area.state,
        'venues':venues
      })

  #Cleaner solution:
  #result = []
  #venues = Venue.query.all()
  #places = Venue.query.distinct(Venue.city, Venue.state).all()
  #for place in places:
  #    tmp_venues = []
  #    for venue in venues:
  #        if venue.city == place.city and venue.state == place.state:
  #            num_upcoming_shows = 0
  #            for show in venue.shows:
  #                if show.start_time > datetime.now():
  #                    num_upcoming_shows += 1
  #            tmp_venues.append({
  #                'id': venue.id,
  #                'name': venue.name,
  #                'num_upcoming_shows': num_upcoming_shows
  #            })
  #    result.append({
  #        'city': place.city,
  #        'state': place.state,
  #        'venues': tmp_venues
  #    })

  return render_template('pages/venues.html', areas=result)

@app.route('/venues/search', methods=['POST']) # Done
def search_venues():
  search_term=request.form['search_term']
  venues=Venue.query.filter(or_(Venue.name.ilike(f'%{search_term}%'),(Venue.city + ', ' + Venue.state)==search_term)).all()
  count=len(venues)

  response={
    "count": count,
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>') # Done
def show_venue(venue_id):
  venue_info = Venue.query.get(venue_id)
  if not venue_info:
    abort(404)
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

@app.route('/venues/create', methods=['POST']) # Done
def create_venue_submission():
  form=VenueForm(request.form)
  error=False

  try:
    data = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website=form.website_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
      )
    db.session.add(data)
    db.session.commit()
  except ValueError as e:
    error=True
    if app.config["ENV"] == "development":
        print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')    
  else:
    flash('Venue ' + form.name.data + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE']) # Done
def delete_venue(venue_id):
  venue=Venue.query.get(venue_id)
  error=False

  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists') # Done
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST']) # Done
def search_artists():
  search_term=request.form['search_term']
  artists=Artist.query.filter(or_(Artist.name.ilike(f'%{search_term}%'),(Artist.city + ', ' + Artist.state) == search_term)).all()
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
    return not_found_error(0)
  
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
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST']) # Done
def edit_artist_submission(artist_id):
  artist=Artist.query.get(artist_id)
  form=ArtistForm(request.form)
  error=False

  try:
    artist.name=form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.genres=form.genres.data
    artist.image_link=form.image_link.data
    artist.facebook_link=form.facebook_link.data
    artist.website=form.website_link.data
    artist.seeking_venue=form.seeking_venue.data
    artist.seeking_description=form.seeking_description.data
    db.session.commit()
  except ValueError as e:
    error=True
    if app.config["ENV"] == "development":
        print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    return abort(500)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET']) # Done
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST']) # Done
def edit_venue_submission(venue_id):
  venue=Venue.query.get(venue_id)
  form=VenueForm(request.form)
  error=False

  try:
    venue.name=form.name.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.address=form.address.data
    venue.phone=form.phone.data
    venue.genres=form.genres.data
    venue.image_link=form.image_link.data
    venue.facebook_link=form.facebook_link.data
    venue.website=form.website_link.data
    venue.seeking_talent=form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data
    db.session.commit()
  except ValueError as e:
    error=True
    if app.config["ENV"] == "development":
        print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    return abort(500)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET']) # Done
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST']) # Done
def create_artist_submission():
  form=ArtistForm(request.form)
  error=False

  try:
    artist=Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.city.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
  except ValueError as e:
    error=True
    if app.config['ENV']=="development":
      print(e)
    db.session.rollback()
  if error:
    flash('An error has occurred. Artist ' + form.name.data + ' was not listed.')
  else:
    flash('Artist ' + form.name.data + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows') # Done
def shows():
  data = Show.query.join(Artist,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).with_entities(Show.venue_id,Venue.name.label('venue_name'),Show.artist_id,Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'),Show.start_time).order_by(Show.start_time.asc()).all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create') # Done
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST']) # Done
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  error=False

  try:
    new_show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
  except ValueError as e:
    error=True
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error has occurred. Show was not listed.')
  else:
    flash('Show was successfully listed!')
  
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
