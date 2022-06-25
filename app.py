import os
import json
import re
import sqlite3
import pprint
from flask import Flask, jsonify, abort, request, g
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

if os.environ.get('DATABASE_URL'):
    path_to_db = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
else:
    path_to_db = f"sqlite:///{BASE_DIR / 'main.db'}"

# path_to_db = "sqlite:////home/agat/Projects/test1/test.db"    # for work
app.config['SQLALCHEMY_DATABASE_URI'] = path_to_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Читаем внешний JSON

with open('data.json') as file:
    items = json.load(file)
    data_list = items.get('data')
    print(data_list)

list_text = []
list_id_str = []
list_id_int = []
for i in range(len(data_list)):
    print(data_list[i])
    list_text.append(data_list[i].get('text'))
    list_id_int.append(data_list[i].get('id_str'))

print(list_text)
print(list_id_str)

num_list = [re.findall('\d+', item)[0] for item in list_id_str]
list_id_int = list(map(int, num_list))
print(list_id_int)


class TableModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(32))
    id_str = db.Column(db.String(32))
    index = db.Column(db.Integer)

    def __init__(self, text, id_str, index):
        self.text = text
        self.id_str = id_str
        self.index = index

    def to_dict(self):
        return {
            "text": self.text,
            "id_str": self.id_str,
            "index": self.index,
        }


db.create_all()


def get_all_table():
    items_in_table = TableModel.query.all()
    spisok = [items_in_table.to_dict() for item in items_in_table]
    return jsonify(spisok)


@app.route("/lists")
def table_list():
    items = TableModel.query.all()
    spisok = [items.to_dict() for item in items]
    return jsonify(spisok), 200


@app.route("/create", methods=["POST"])
def create_pole():
    author_data = request.json
    author = TableModel(**author_data)
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201


#
#
# # QUOTES
# #                      .to_dict()        jsonify()
# # Сериализация: object ----------> dict ----------> json
# @app.route("/quotes")
# def quotes_list():
#     # authors = AuthorModel.query.all()
#     quotes = QuoteModel.query.all()
#     quotes = [quote.to_dict() for quote in quotes]
#     return jsonify(quotes), 200
#

#
#
# @app.route("/authors/<int:author_id>/quotes", methods=["POST"])
# def create_quote(author_id):
#     author = AuthorModel.query.get(author_id)
#     new_quote = request.json
#     q = QuoteModel(author, new_quote["text"])
#     db.session.add(q)
#     db.session.commit()
#     return jsonify(q.to_dict()), 201
#
#
# @app.route("/quotes/<int:quote_id>", methods=['PUT'])
# def edit_quote(quote_id):  # author text
#     new_data = request.json
#     quote = QuoteModel.query.get(quote_id)
#     if quote is None:
#         abort(404)
#     # quote.text = new_data.get("text", quote.text)
#     # quote.author = new_data.get("author", quote.author)
#     for key, value in new_data.items():
#         setattr(quote, key, value)
#     db.session.commit()  # SQL --> UPDATE
#     return jsonify(quote.to_dict()), 200
#
#
# @app.route("/quotes/<int:quote_id>", methods=['DELETE'])
# def delete(quote_id):
#     quote = QuoteModel.query.get(quote_id)
#     if quote is None:
#         abort(404)
#     db.session.delete(quote)
#     db.session.commit()
#     return f"Quote with id={quote_id} is deleted.", 200


if __name__ == "__main__":
    app.run(debug=True)
