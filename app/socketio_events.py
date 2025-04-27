from flask_socketio import join_room, leave_room, send, emit
from flask_login import current_user
from app.models import Message
from .extensions import mongo
from flask import request

# This function should be called in __init__.py to register all events
def register_socketio_events(socketio):

    @socketio.on("connect")
    def handle_connect():
        if current_user.is_authenticated:
            print(f"{current_user.username} connected.")
        else:
            print("An anonymous user connected.")

    @socketio.on("disconnect")
    def handle_disconnect():
        if current_user.is_authenticated:
            print(f"{current_user.username} disconnected.")
        else:
            print("An anonymous user disconnected.")

    @socketio.on("join_room")
    def handle_join_room(data):
        print(f"[DEBUG] Received join_room data: {data}")
        room = data.get("room")
        username = data.get("username", "Anonymous")

        if not room:
            emit("error", {"message": "Room not specified."})
            return

        join_room(room)

        # Broadcast join message
        emit("message", {
            "username": "System",
            "message": f"{username} has joined the room."
        }, room=room)

        # Send chat history to the newly joined user
        messages = Message(mongo).get_messages_by_room(room)
        for msg in messages:
            emit("message", {
                "username": msg.get("sender", "Unknown"),
                "message": msg["content"] + (" [edited]" if msg.get("edited") else ""),
                "message_id": str(msg["_id"]),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else ""
            }, to=request.sid)


    @socketio.on("leave_room")
    def handle_leave_room(data):
        room = data["room"]
        username = current_user.username if current_user.is_authenticated else "Guest"
        leave_room(room)
        # send(f"{username} has left the room: {room}", to=room)
        emit("message", {"username": "System", "message": f"{username} has left the room: {room}"}, to=room)
        print(f"{username} left room {room}")

    @socketio.on("message")
    def handle_message(data):
        room = data["room"]
        message = data["message"]
        username = current_user.username if current_user.is_authenticated else "Guest"
        
        message_id = Message(mongo).save_message(room, username, message)
        emit("message", {
            "username": username,
            "message": message,
            "message_id": message_id
        }, to=room)

    @socketio.on("edit_message")
    def handle_edit(data):
        msg_id = data["message_id"]
        new_content = data["new_content"]
        username = current_user.username

        if not msg_id or len(msg_id) != 24:  # Ensure valid ObjectId format
            emit("error", {"message": "Invalid message ID."}, to=request.sid)
            return
        
        if Message(mongo).is_owner(msg_id, username):
            Message(mongo).update_message(msg_id, new_content)
            emit("message_edited", {"message_id": msg_id, "new_content": new_content + " [edited]",  "username": username}, broadcast=True)
        else:
            emit("error", {"message": "You are not allowed to edit this message."}, to=request.sid)

    @socketio.on("delete_message")
    def handle_delete(data):
        msg_id = data["message_id"]
        username = current_user.username

        if not msg_id or len(msg_id) != 24:  # Ensure valid ObjectId format
            emit("error", {"message": "Invalid message ID."}, to=request.sid)
            return

        if Message(mongo).is_owner(msg_id, username):
            # Overwrite content in DB
            Message(mongo).update_message(msg_id, "This message was deleted.")

            # Notify all clients to update this message visually
            emit("message_edited", {
                "message_id": msg_id,
                "new_content": "<em class='text-muted'>This message was deleted.</em>",
                "username": username  # Needed for client to render correctly
            }, broadcast=True)
        else:
            emit("error", {"message": "You are not allowed to delete this message."}, to=request.sid)