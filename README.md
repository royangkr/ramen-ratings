# Ramen Ratings API

## Design considerations
I want all the data provided in the sample dataset to be included in the database. As such, I assume all the rows in the sample dataset are valid i.e.
- ID need not be unique, but must not be NULL
- [Country must be found in the ISO 3166-1]
- Type can be NULL
- Package can be NULL
- Rating, while usually between 0.0-5.0, could contain invalid data such as #VALUE! or NULL

Importantly, I decided to not use ID as the primary key and instead use the [unique rowid]. This gave me the opportunity to use the ID as the “ID/token of the reviewer”. When submitting reviews, the reviewer is asked to include an ID. If someone wants to modify/delete the review, he has to enter the correct ID.

## Installation for Windows
Install [Python 3]
Enter the project directory, create a virtual env and enter it
```
cd ramen_ratings
py -m pip install --upgrade pip
py -m pip install --user virtualenv
py -m venv env
.\env\Scripts\activate
```
Install dependencies
```
py -m pip install -r requirements.txt
```

## Running the server
```
python init_db.py
set FLASK_APP=app.py
flask run
```
#### On the use of curl and Postman
For the rest of this documentation, I will be demonstrating using Windows command prompt and Postman. The commands will work in Windows Powershell if [use curl.exe instead of curl] and [--% to stop parsing as powershell commands]:
```
curl.exe --%
```

## List all reviews
Endpoint: http://127.0.0.1:5000/reviews, HTTP Method: GET
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews
```
On Postman
![list result](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/listreviews.PNG "list result")

## Create a new review
Endpoint: http://127.0.0.1:5000/reviews, HTTP Method: POST
ID, Country and Brand are required and cannot be empty. [Country must be found in the ISO 3166-1]
To create a review with 
| ID | Country | Brand | Type | Package | Rating |
| ------ | ------ | ------ | ------ | ------ | ------ |
| 3000 | SGP | Brand A | Laksa | Cup | 4.9 |
On Postman, send POST to http://127.0.0.1:5000/reviews and use the following as Body input
`{"ID":"3000","Country":"SGP","Brand":"Brand A","Type":"Laksa","Package":"Cup","Rating":4.9}`
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews -X POST -H "Content-Type: application/json" -d "{\"ID\":\"3000\", \"Country\": \"SGP\", \"Brand\": \"Brand A\",\"Type\": \"Laksa\",\"Package\": \"Cup\",\"Rating\": \"4.9\"}"
```
![create result](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/createReview.PNG "create result")

## Get specific review
Endpoint: http://127.0.0.1:5000/reviews/<rowid>, HTTP Method: GET
On Postman, send GET to http://127.0.0.1:5000/reviews/1
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews/1
```
![getReview](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/getReview.PNG "getReview")
## Modify review
Endpoint: http://127.0.0.1:5000/reviews/<rowid>, HTTP Method: PUT or PATCH
ID must match the one used when review was created.
#### PUT (replaces all columns)
Country and Brand are required and cannot be empty. [Country must be found in the ISO 3166-1]
On Postman, send PUT to http://127.0.0.1:5000/reviews/1 and use the following as Body input
`{“ID”:“1”,“Country”:“SGP”,“Brand”:“Brand A”,“Type”:“Laksa”,“Package”:“Cup”,“Rating”:4.9}`
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews/1 -X PUT -H "Content-Type: application/json" -d "{\"ID\":\"1\", \"Country\": \"SGP\", \"Brand\": \"Brand A\",\"Type\": \"Laksa\",\"Package\": \"Cup\",\"Rating\": \"4.9\"}"
```
![putReview](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/putReview.PNG "putReview")
#### PATCH (changes some columns)
Country and Brand are not required but cannot be empty. [Country must be found in the ISO 3166-1]
On Postman, send PATCH to http://127.0.0.1:5000/reviews/1 and use the following as Body input
`{“ID”:“1”,“Rating”:4.8}`
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews/1 -X PATCH -H "Content-Type: application/json" -d "{\"ID\":\"1\",\"Rating\": \"4.8\"}"
```
![patchReview](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/patchReview.PNG "patchReview")
## Delete review
Endpoint: http://127.0.0.1:5000/reviews/<rowid>, HTTP Method: DELETE
ID must match the one used when review was created.
On Postman, send DELETE to http://127.0.0.1:5000/reviews/1 and use the following as Body input
`{“ID”:“1”}`
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews/1 -X DELETE -H "Content-Type: application/json" -d "{\"ID\":\"1\"}"
```
![deleteReview](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/deleteReview.PNG "deleteReview")
## Get a list of ramen reviews filtered by a country
Endpoint: http://127.0.0.1:5000/reviews?countr=<country>, HTTP Method: GET
##### Restriction on Country value
When reviews are created, the Country value must be found in the ISO 3166-1, a standard defining codes for the names of countries. 
For example, Singapore in the ISO 3166-1 is `Country(name='Singapore', alpha2='SG', alpha3='SGP', numeric='702')`. The name or codes are accepted and when filtered by country, any row with County that matches name or code (no need to match case) will be shown.
Accepted values: `SGP, sgp, sGp, Singapore, siNgapore, SG, sg, 702` etc
Unaccepted/Wrong values: `Singapo, ingapore, s, gp(points to Guadeloupe)` etc
Notably, in the sample dataset, only Country "UK" does not match any of the countries in ISO 3166-1. Tha is becuase United Kingdom is `Country(name='United Kingdom of Great Britain and Northern Ireland', alpha2='GB', alpha3='GBR', numeric='826')`. I manually added it as an acceptable value.
On Postman, send GET to http://127.0.0.1:5000/reviews?country=GB
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews?country=GB
```
![listCountry](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/listCountry.PNG "listCountry")
## Get a list of ramen reviews based on a partial text
Endpoint: http://127.0.0.1:5000/reviews?q=<partial text>, HTTP Method: GET
On Postman, send GET to http://127.0.0.1:5000/reviews?q=Seaweed
On Windows Command Prompt
```
curl -i http://127.0.0.1:5000/reviews?q=Seaweed
```
![listQuery](https://github.com/royangkr/ramen-ratings/raw/main/screenshots/listQuery.PNG "listQuery")


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [Python 3]: <https://www.python.org/downloads/>
   [use curl.exe instead of curl]: <https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwipkcrgjIL4AhXDW3wKHSuzCVIQFnoECBAQAw&url=https%3A%2F%2Fwww.delftstack.com%2Fhowto%2Fpowershell%2Frun-curl-command-via-powershell%2F%23%3A~%3Atext%3Dthe%2520curl%2520in%2520Windows%2520PowerShell%2Cto%2520the%2520Invoke%252DWebRequest%2520cmdlet.&usg=AOvVaw1gDd4xaskqQb9CzNHIJANZ>
   [--% to stop parsing as powershell commands]: <https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parsing?view=powershell-7.2#the-stop-parsing-token>
   [unique rowid]:https://www.sqlite.org/rowidtable.html
   [Country must be found in the ISO 3166-1]:#restriction-on-country-value