from app import contestplatform
contestplatform.socketio.run(contestplatform,host="0.0.0.0", debug=True, port="9000")