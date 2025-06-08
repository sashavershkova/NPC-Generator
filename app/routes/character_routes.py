from flask import Blueprint, request, abort, make_response
from ..db import db
from ..models.character import Character
from ..models.greeting import Greeting
from sqlalchemy import func, union, except_
from ..models.utilities import generate_greetings
import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

bp = Blueprint("characters", __name__, url_prefix="/characters")

@bp.post("")
def create_character():

    request_body = request.get_json()
    try: 
        new_character = Character.from_dict(request_body)
        db.session.add(new_character)
        db.session.commit()

        return new_character.to_dict(), 201
    
    except KeyError as e:
        abort(make_response({"message": f"missing required value: {e}"}, 400))

@bp.get("")
def get_characters():
    character_query = db.select(Character)

    characters = db.session.scalars(character_query)
    response = []

    for character in characters:
        response.append(
            {
                "id" : character.id,
                "name" : character.name,
                "personality" : character.personality,
                "occupation" : character.occupation,
                "age" : character.age
            }
        )

    return response

@bp.get("/<char_id>/greetings")
def get_greetings(char_id):
    character = validate_model(Character, char_id)
    
    if not character.greetings:
        return {"message": f"No greetings found for {character.name} "}, 201
    
    response = {"Character Name" : character.name,
                "Greetings" : []}
    for greeting in character.greetings:
        response["Greetings"].append({
            "greeting" : greeting.greeting_text
        })
    
    return response


@bp.post("/<char_id>/generate")
def add_greetings(char_id):
    character = validate_model(Character, char_id)
    greetings_texts = generate_greetings(character)

    if character.greetings:
        return {"message" : f"Greetings for {character.name} already generated: {character.greetings}"}
    
    greetings_instances_list = []
    for text in greetings_texts:
        new_greeting = Greeting(greeting_text=text, character=character)
        greetings_instances_list.append(new_greeting)

    db.session.add_all(greetings_instances_list)
    db.session.commit()

    return {"message" : f"Greetings for {character.name} successfully generated!"}, 201

def validate_model(cls,id):
    try:
        id = int(id)
    except:
        response = {"message": f"{cls.__name__} {id} invalid"}
        abort(make_response(response , 400))

    query = db.select(cls).where(cls.id == id)
    model = db.session.scalar(query)
    if model:
        return model

    response = {"message": f"{cls.__name__} {id} not found"}
    abort(make_response(response, 404))