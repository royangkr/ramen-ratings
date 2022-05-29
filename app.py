# app.py
import sqlite3
import json
from flask import Flask, request,jsonify, abort
from iso3166 import countries

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    
def query_review(review_rowid):
    conn = get_db_connection()
    review = conn.execute('SELECT rowid,* FROM reviews WHERE rowid = ?',
                        (review_rowid,)).fetchone()
    conn.close()
    return review

def process_new_review(review):
    if 'Country' in review:
        country = review['Country']
        try:
            countries.get(review['Country'])
        except KeyError:
            if review['Country']!='UK':
                return {"error":str(review['Country'])+" is not found in ISO 3166-1 Country definitions"}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
    else:
        return {"error":"Country is required"}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
    ID=review.get('ID')
    brand=review.get('Brand')
    typeName = review.get('Type')
    packageName = review.get('Package')
    rating = review.get('Rating')
    return [ID, country, brand, typeName, packageName, rating]

@app.get("/reviews")
def get_reviews():
    args=request.args.to_dict()
    if 'country' in args:
        UK=False
        if args['country']=='UK':
            args['country']='GB'
        try:
            c=countries.get(args['country'])
        except KeyError:
            return {"error":str(args['country'])+" is not found in ISO 3166-1 Country definitions"}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        if c.alpha2=='GB':
            UK=True
        conn = get_db_connection()
        reviews = conn.execute('SELECT rowid, Country, Brand, Type, Package, Rating FROM reviews'
                               ' WHERE upper(Country)=upper(?) OR upper(Country)=upper(?) OR upper(Country)=upper(?) OR upper(Country)=upper(?) OR Country=?', #search for country that matches any of the codes without needing to match case
                               (c.name,c.alpha2,c.alpha3,c.apolitical_name,c.numeric)).fetchall()
        result=[dict(ix) for ix in reviews]
        if UK:
            reviews = conn.execute('SELECT rowid, Country, Brand, Type, Package, Rating FROM reviews WHERE Country=\'UK\'').fetchall()
            for r in reviews:
                result.append(dict(r))
        conn.close()
        return jsonify(result)
    if 'q' in args:
        query=args['q']
        conn = get_db_connection()
        reviews = conn.execute('SELECT rowid, Country, Brand, Type, Package, Rating FROM reviews WHERE instr(Type, ?)>0', #if query text is found in Type data
                              (query,)).fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in reviews])
    conn = get_db_connection()
    reviews = conn.execute('SELECT rowid, Country, Brand, Type, Package, Rating FROM reviews').fetchall() #hide id since it is used as token
    conn.close()
    return jsonify([dict(ix) for ix in reviews])
    
@app.post("/reviews")
def add_review():
    if request.is_json:
        review = request.get_json()
        result=process_new_review(review)
        print(len(result))
        if len(result)!=6:
            return result
        conn = get_db_connection()
        cursor=conn.cursor()
        try:
            cursor.execute("INSERT INTO reviews (ID, Country, Brand, Type, Package, Rating) VALUES (?, ?, ?, ?, ?, ?)",
                           (result[0],result[1],result[2],result[3],result[4],result[5]))
        except sqlite3.IntegrityError as e:
            return {"error":str(e)}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        conn.commit()
        conn.close()
        return jsonify(dict(query_review(cursor.lastrowid))), 201
    return {"error": "Request must be JSON"}, 415

@app.get("/reviews/<rowid>")
def get_review(rowid):
    review=query_review(rowid)
    if not review:
        return {"error": "Review "+str(rowid)+" not found"}, 404
    result=dict(review)
    result.pop('ID') #hide id since it is used as token
    return jsonify(result)

@app.delete("/reviews/<rowid>")
def delete_review(rowid):
    review=query_review(rowid)
    if not review:
        return {"error": "Review "+str(rowid)+" not found"}, 404
    if request.is_json:
        request_review = request.get_json()
        if 'ID' in request_review:
            if request_review['ID']==review['ID']:
                conn = get_db_connection()
                conn.execute('DELETE FROM reviews WHERE rowid = ?', (rowid,))
                conn.commit()
                conn.close()
                return {}, 200 #Successful request
            else:
                return {"error":"Wrong ID"}, 401 # Unauthorized
        else:
            return {"error":"ID is required"}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
    return {"error": "Request must be JSON"}, 415 #Unsupported Media Type
    
@app.put("/reviews/<rowid>")
def update_review(rowid):
    old_review=query_review(rowid)
    if not old_review:
        return {"error": "Review "+str(rowid)+" not found"}, 404
    if request.is_json:
        review = request.get_json()
        if 'ID' in review:
            if review['ID']!=old_review['ID']:
                return {"error":"Wrong ID"}, 401 # Unauthorized
        else:
            return {"error":"ID is required"}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        result=process_new_review(review)
        if len(result)!=6:
            return result
        conn = get_db_connection()
        cursor=conn.cursor()
        try:
            cursor.execute('UPDATE reviews SET Country = ?, Brand = ?, Type = ?, Package = ?, Rating = ?'
                           ' WHERE rowid = ?',
                           (result[1],result[2],result[3],result[4],result[5], rowid))
        except sqlite3.IntegrityError as e:
            return {"error":str(e)}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        conn.commit()
        conn.close()
        return jsonify(dict(query_review(rowid))), 200
    return {"error": "Request must be JSON"}, 415 #Unsupported Media Type

@app.patch("/reviews/<rowid>")
def patch_review(rowid):
    old_review=query_review(rowid)
    if not old_review:
        return {"error": "Review "+str(rowid)+" not found"}, 404
    if request.is_json:
        review = request.get_json()
        if 'ID' in review:
            if review['ID']!=old_review['ID']:
                return {"error":"ID does not match"}, 401 # Unauthorized
        else:
            return {"error":"ID is required"}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        conn = get_db_connection()
        cursor=conn.cursor()
        if 'Country' in review:
            country = review['Country']
            try:
                countries.get(review['Country'])
            except KeyError:
                if review['Country']!='UK':
                    return {"error":"Country not found in ISO 3166-1 Country definitions"}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
            cursor.execute('UPDATE reviews SET Country = ?'
                           ' WHERE rowid = ?',
                           (country, rowid))
        if 'Brand' in review:
            brand = review['Brand']
            try:
                cursor.execute('UPDATE reviews SET Brand = ?'
                               ' WHERE rowid = ?',
                               (brand, rowid))
            except sqlite3.IntegrityError as e:
                return {"error":str(e)}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        if 'Type' in review:
            typeName = review['Type']
            try: 
                cursor.execute('UPDATE reviews SET Type = ?'
                               ' WHERE rowid = ?',
                               (typeName, rowid))
            except sqlite3.IntegrityError as e:
                return {"error":str(e)}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        if 'Package' in review:
            packageName = review['Package']
            try:
                cursor.execute('UPDATE reviews SET Package = ?'
                               ' WHERE rowid = ?',
                               (packageName, rowid))
            except sqlite3.IntegrityError as e:
                return {"error":str(e)}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        if 'Rating' in review:
            rating = review['Rating']
            try: 
                cursor.execute('UPDATE reviews SET Rating = ?'
                               ' WHERE rowid = ?',
                               (rating, rowid))
            except sqlite3.IntegrityError as e:
                return {"error":str(e)}, 422 #Unprocessable Entity. The request data was properly formatted but contained invalid or missing data.
        conn.commit()
        conn.close()
        return jsonify(dict(query_review(rowid))), 200
    return {"error": "Request must be JSON"}, 415 #Unsupported Media Type
