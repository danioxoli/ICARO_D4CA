// ---- Module Imports ----

var http = require('https'); // Secure HTTP
var fs = require('fs'); // File system 
var mongo = require('mongodb'); // MongoDB Driver
var Curl = require('node-libcurl').Curl;
// ---- Connection to MongoDB Server and Database ----



var url = 'mongodb://localhost:your_database';

function insertData(myData) {
    mongo.connect(url, function(err, db) {
        console.log("Connected successfully to server");
        insertDocument(db, myData, function() {
            db.close();
        });
    });
}
var insertDocument = function(db, data, callback) {
    db.collection('events').insertOne(data, function(err, result) {
        callback();
    });
};


function processData(result) {
    
    try {
        result=JSON.parse(result);
       
        var jams = result.jams;
        var irregularities = result.irregularities;
        var myData = {};
        if (jams)
            myData.jams = jams;
        if (irregularities)
            myData.irregularities = irregularities;

        myData.timeStamp = result.startTimeMillis;


    } catch (e) {
        console.log("Exception thrown: " + e.message);
    }

    insertData(myData);
}


function query() {

    var link = "https://world-georss.waze.com/rtserver/web/TGeoRSS?tk=ccp_partner&ccp_partner_name=%yourname&format=JSON&types=traffic,alerts&muao=true&polygon=8.654000,45.865000;9.805000,45.867000;9.836000,45.201000;8.649000,45.215000;8.654000,45.865000;8.654000,45.865000";
    console.log("parte query");
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


setInterval(function(){
query();
},1800000);