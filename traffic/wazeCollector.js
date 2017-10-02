// ---- Module Imports ----
var http = require('https'); // Secure HTTP
var fs = require('fs'); // File system 
var mongo = require('mongodb'); // MongoDB Driver
var Curl = require('node-libcurl').Curl;
// ---- Connection to MongoDB Server and Database ----

var url = 'mongodb://localhost:your_database';

//This function insert some data in the appropriate collection
function insertData(myData) {
    mongo.connect(url, function(err, db) {
        console.log("Connected successfully to server");
        insertDocument(db, myData, function() {
            db.close();
        });
    });
}
//You can change 'events' with your own table, or leave it as it is to create a new 'events' table
var insertDocument = function(db, data, callback) {
    db.collection('events').insertOne(data, function(err, result) {
        callback();
    });
};

//This function process the data, by extracting the field we are interested in
function processData(result) {
    try {
        result=JSON.parse(result);
        
        var jams = result.jams;
        var irregularities = result.irregularities;
        //Create a new object myData to contain the fields we interested into
        var myData = {};
        
        if (jams)
            myData.jams = jams;
        if (irregularities)
            myData.irregularities = irregularities;

        myData.timeStamp = result.startTimeMillis;

    } catch (e) {
        console.log("Exception thrown: " + e.message);
    }
//when the object myData is ready, we can insert it into the database
    insertData(myData);
}

//Set a function to query the API for data with a simple Curl request
function query() {
    var link = "https://world-georss.waze.com/rtserver/web/TGeoRSS?tk=ccp_partner&ccp_partner_name=%yourname&format=JSON&types=traffic,alerts&muao=true&polygon=%yourBBOX%";

    var requests = new Curl();
    requests.setOpt('URL', link);
    requests.setOpt('FOLLOWLOCATION', true);
    requests.on('end', function(statusCode, body, headers) {
        if (body && JSON.parse(body)) {
            processData(body);
        }
    });
    requests.on('error', requests.close.bind(requests));
    requests.perform();
}

//Run the query every 30 minutes
setInterval(function(){
query();
},1800000);
