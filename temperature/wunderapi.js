//Nodejs requirements files
var express = require('express');
var app = express();
var Curl = require('node-libcurl').Curl;
var sleep = require('system-sleep');
var json2csv = require('json2csv');
var fs = require('fs');


//Fields of the CSV to create
var fields = ['lat', 'lng', 'name', 'date', 'tmp', 'hum', 'prec', 'heatindex'];
//Start date to query for the data
var startDate = "01/01/2016";
//An array of stations in the specified format. Should be filled with the ones you are interested into
var stations = [{"id": STATIONID, "lat": LATITUDE, "lon": LONGITUDE}];
//First day to start from
var indexDay = 0;
// First station to start from
var stationIndex = 0;
var requests = [];
requests[stationIndex] = [];

//Initialize some variables
var obs = null;
var csv = [];


//Set the init date to download the files with WunderAPI
var InitDate = new Date(startDate);


//Function to increase one day and return it in the WunderAPI format
function getDay() {
    var dayPlus = 86400000;
    InitDate.setMilliseconds(dayPlus);
    var year = InitDate.getFullYear();
    var day = InitDate.getDate();
    if (day < 10) {
        day = "0" + day;
    }
    var month = InitDate.getMonth() + 1;
    if (month < 10) {
        month = "0" + month;
    }
    return (String(year) + String(month) + String(day));
}

//Function to query WunderAPI inserting the available stations and their position
function query() {
    var date = getDay();
    var station = stations[stationIndex].id;

    var link = "api.wunderground.com/api/myKey/history_" + date + "/q/pws:" + station + ".json";

    requests[stationIndex][indexDay] = new Curl();
    requests[stationIndex][indexDay].setOpt('URL', link);
    requests[stationIndex][indexDay].setOpt('FOLLOWLOCATION', true);
    requests[stationIndex][indexDay].on('end', function (statusCode, body, headers) {
        try {

            if (body && JSON.parse(body) && JSON.parse(body).history && JSON.parse(body).history.observations) {
                var obs = JSON.parse(body).history.observations;

                for (var x = 0; x < obs.length; x++) {

                    var y = obs[x].date.year;
                    var m = obs[x].date.mon;
                    var d = obs[x].date.mday;
                    var time = new Date(m + "/" + d + "/" + y);
                    time.setHours(obs[x].date.hour);
                    time.setMinutes(obs[x].date.min);
                    time = time.toISOString();


                    obj = {
                        "lat": stations[stationIndex].lat,
                        "lng": stations[stationIndex].lon,
                        "name": stations[stationIndex].id,
                        "date": time,
                        "tmp": obs[x].tempm,
                        "hum": obs[x].hum,
                        "prec": obs[x].precip_totalm,
                        "heatindex": obs[x].heatindexm
                    };

                    csv.push(obj);
                }
                console.log("Pushed date: " + date + " On station: " + stations[stationIndex].id);
                if (indexDay < 365) { //Query only X days (365 now)
                    indexDay++;
                    sleep(10000); // sleep for ten seconds (rate limit 10 calls per minute)
                    query();
                } else if (stationIndex < stations.length) {
                    //Restart from day one, but with the next station
                    indexDay = 1;
                    save(csv, station);
                    csv = [];
                    InitDate = new Date(startDate);
                    stationIndex++;
                    console.log(stationIndex);
                    sleep(10000);
                    if (stationIndex < stations.length) {
                        requests[stationIndex] = [];
                        query();
                    }
                    else
                        console.log("Finished");
                } else {

                }
            } else {
                stationIndex++;
                query();
            }
        } catch (e) {
            console.log("Error:");
            console.log(e);
            stationIndex++;
            query();
        }
        this.close();
    });
    requests[stationIndex][indexDay].on('error', requests[stationIndex][indexDay].close.bind(requests[stationIndex][indexDay]));
    requests[stationIndex][indexDay].perform();
}

//function to create a CSV after one station has finished to be queried
function save(csv, station) {
    try {
        json2csv({
            data: csv,
            fields: fields
        }, function (err, csv) {
            if (err) console.log(err);
            fs.writeFile('csv/' + station + '.csv', csv, function (err) {
                if (err) throw err;
                console.log('file saved');
            });
        });
    } catch (e) {
        console.log("Error writing: " + e)
    }
}

//Calling to the main function, that will call itself after each station
query();

//Running node.js app
app.listen(3000, function () {
    console.log('App started');
});
