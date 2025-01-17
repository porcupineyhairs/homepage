from flask import render_template, flash, redirect, send_file, url_for, jsonify
from home import app, redis_store, twilio
from home.frontend import frontend

FINISH_COUNT = 60

@frontend.route('/slaptext/<phone_num_str>', methods=['POST'])
def send_sms_slap(phone_num_str):
    body='\xF0\x9F\x98\xA7\xF0\x9F\x91\x8B'
    message = twilio.messages.create(to="+1"+phone_num_str,
                                     from_="+15412348051",
                                     body=body)
    return jsonify({"message": "sent slap"}), 201

@frontend.route('/runner/<runner_name>', methods=['POST'])
def update_runner(runner_name):
    state = redis_store.get('state')
    if state == 'pre_race':
        redis_store.set(runner_name, 0)
        redis_store.sadd('runners', runner_name)
    elif state == 'racing':
        print "racing"
        if redis_store.sismember('runners', runner_name)==1:
            print("sismember")
            count = redis_store.get(runner_name)
            print(count)
            if int(count) < FINISH_COUNT:
                print("incrementing")
                redis_store.incr(runner_name)
    return jsonify({runner_name: redis_store.get(runner_name)})

@frontend.route('/slapdash', methods=['GET', 'POST'])
def show_slapdash():
    redis_store.delete('runners')
    redis_store.set('state', 'pre_race')
    return render_template('slapdash.html')

@frontend.route('/slapdash/init', methods=['GET','POST'])
def init_slapdash():
    redis_store.delete('runners')
    redis_store.set('state', 'pre_race')
    return jsonify({'message': 'building field'})

@frontend.route('/slapdash/start', methods=['POST'])
def start_race():
    redis_store.set('state', 'racing')
    return jsonify({'message': 'starting'})

@frontend.route('/slapdash/update', methods=['GET'])
def update_slapdash():
    runners = []
    for member in redis_store.smembers('runners'):
        runners.append({'name':member, 'pos': redis_store.get(member)})
    return jsonify({'state': redis_store.get('state'), 'runners':runners})

@frontend.route('/test_api', methods=['GET'])
def test_api():
    return jsonify({"message": "hello!"})

@frontend.route('/test_post', methods=['POST'])
def test_post():
    return jsonify({"message": "posted!"}), 201

@frontend.route('/', methods=['GET'])
@frontend.route('/index', methods=['GET'])
def index():
    return render_template('index.html',
                            title='Home')

@frontend.route('/resume')
def get_resume():
    return render_template('resume.html',
                            title='Resume')

@frontend.route('/download/<path:filename>')
def download(filename):
    flash("Downloading " + '/'.join(['static','download', filename]))
    return send_file('/'.join(['static','download', filename]))
