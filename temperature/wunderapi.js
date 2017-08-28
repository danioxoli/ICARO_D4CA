//Nodejs requirements files
var express = require('express');
var app = express();
var Curl = require('node-libcurl').Curl;
var sleep = require('system-sleep');
var json2csv = require('json2csv');
var fs = require('fs');

//Default values

//Fields of the CSV to create
var fields = ['lat', 'lng', 'name', 'date', 'tmp', 'hum', 'prec', 'heatindex'];

//Initialize the observations to null
var obs = null;

//Set the init date to download the files with WunderAPI
var InitDate = new Date("01/01/2016");


//Function to increase one day and return in in the WunderAPI format
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

var indexDay = 1;
var stationIndex = 37;

var csv = [];
var stations = [{"id": "ILOMBARD205", "lat": "45.49529648", "lon": "9.13592434"}, {
    "id": "ILOMBARD204",
    "lat": "45.45364761",
    "lon": "9.13336372"
}, {"id": "ILOMBARD268", "lat": "45.52049637", "lon": "9.05040646"}, {
    "id": "IMILAN164",
    "lat": "45.46670151",
    "lon": "9.19999981"
}, {"id": "ILOMBARD77", "lat": "45.39311600", "lon": "9.28469276"}, {
    "id": "ILOMBARD329",
    "lat": "45.47095490",
    "lon": "9.21825981"
}, {"id": "IMILANOM4", "lat": "45.49798965", "lon": "9.24054241"}, {
    "id": "ILOMBARD306",
    "lat": "45.42748642",
    "lon": "9.09533501"
}, {"id": "LIML", "lat": "45.43000031", "lon": "9.27999973"}, {
    "id": "WMO16081",
    "lat": "45.45999908",
    "lon": "9.25833321"
}, {"id": "IMILAN163", "lat": "45.49780655", "lon": "9.19624329"}, {
    "id": "IMILAN15",
    "lat": "45.52760315",
    "lon": "9.20876408"
}, {"id": "ILMCITTA6", "lat": "45.47975922", "lon": "9.23264790"}, {
    "id": "ILMAFFOR4",
    "lat": "45.50021744",
    "lon": "9.19061184"
}, {"id": "IMILANO606", "lat": "45.51649475", "lon": "9.19090271"}, {
    "id": "IMILANO501",
    "lat": "45.46146393",
    "lon": "9.22147655"
}, {"id": "IMILAN26", "lat": "45.48268890", "lon": "9.16331196"}, {
    "id": "IMILANO738",
    "lat": "45.42832947",
    "lon": "9.17338276"
}, {"id": "INOVATEM11", "lat": "45.53082657", "lon": "9.13855171"}, {
    "id": "IVIMODRO10",
    "lat": "45.52298737",
    "lon": "9.27673721"
}, {"id": "IMILANO37", "lat": "45.43643570", "lon": "9.24158764"}, {
    "id": "IMILANO324",
    "lat": "45.49585342",
    "lon": "9.10442924"
}, {"id": "IRHO16", "lat": "45.53264618", "lon": "9.03961182"}, {
    "id": "IMILAN136",
    "lat": "45.49313736",
    "lon": "9.15416718"
}, {"id": "ICUSAGO2", "lat": "45.45210266", "lon": "9.04073334"}, {
    "id": "IARESE10",
    "lat": "45.54294205",
    "lon": "9.07763004"
}, {"id": "IROZZANO6", "lat": "45.40044022", "lon": "9.15784264"}, {
    "id": "IMILAN5762",
    "lat": "45.46103287",
    "lon": "9.08264828"
}, {"id": "IMILANO634", "lat": "45.43708038", "lon": "9.18206501"}, {
    "id": "ILMCOLOG2",
    "lat": "45.53498077",
    "lon": "9.28606987"
}, {"id": "ISESTOSA11", "lat": "45.54383087", "lon": "9.23800087"}, {
    "id": "IMILANO621",
    "lat": "45.45168686",
    "lon": "9.17781544"
}, {"id": "IMILANO519", "lat": "45.51147079", "lon": "9.17359829"}, {
    "id": "IBUCCINA3",
    "lat": "45.42278290",
    "lon": "9.11785126"
}, {"id": "IMILANO51", "lat": "45.46987915", "lon": "9.13912106"}, {
    "id": "IBUCCINA6",
    "lat": "45.42168427",
    "lon": "9.07919121"
}, {"id": "ISANDONA3", "lat": "45.41212463", "lon": "9.26596355"}, {
    "id": "IMILANO274",
    "lat": "45.49269104",
    "lon": "9.22008514"
}, {"id": "IMILANO505", "lat": "45.45698166", "lon": "9.11863136"}, {
    "id": "IMILAN131",
    "lat": "45.52869797",
    "lon": "9.19394779"
}, {"id": "IMILANO24", "lat": "45.52246475", "lon": "9.16901970"}, {
    "id": "IMILAN128",
    "lat": "45.44615555",
    "lon": "9.19289303"
}, {"id": "IMILANO95", "lat": "45.43764496", "lon": "9.22531128"}, {
    "id": "ILMMONCU13",
    "lat": "45.45617676",
    "lon": "9.15516663"
}, {"id": "ILMCRESC6", "lat": "45.52864456", "lon": "9.24835873"}, {
    "id": "IMILANO21",
    "lat": "45.51506042",
    "lon": "9.21111012"
}, {"id": "IMILANO486", "lat": "45.50227737", "lon": "9.17613220"}, {
    "id": "ISEGRATE29",
    "lat": "45.50526428",
    "lon": "9.27040005"
}, {"id": "ILMCITTA16", "lat": "45.47946930", "lon": "9.21916389"}, {
    "id": "IMILANLI3",
    "lat": "45.45449829",
    "lon": "9.24910164"
}, {"id": "ISANGIUL11", "lat": "45.38223648", "lon": "9.21450424"}, {
    "id": "ILMCESAN2",
    "lat": "45.45087051",
    "lon": "9.10361195"
}, {"id": "IMILANO555", "lat": "45.44149780", "lon": "9.14750004"}, {
    "id": "ILMVIGHI2",
    "lat": "45.49777603",
    "lon": "9.04286861"
}, {"id": "IMILANO84", "lat": "45.43980408", "lon": "9.11983776"}, {
    "id": "IMILANO618",
    "lat": "45.50822067",
    "lon": "9.14579391"
}, {"id": "INOVATEM3", "lat": "45.54568863", "lon": "9.13591290"}, {
    "id": "IBRESSO12",
    "lat": "45.53978729",
    "lon": "9.18445206"
}, {"id": "ILMMAZZO2", "lat": "45.53226089", "lon": "9.06650543"}, {
    "id": "ILMBUCCI2",
    "lat": "45.41826248",
    "lon": "9.10212040"
}, {"id": "IMILANO356", "lat": "45.41958618", "lon": "9.15944958"}, {
    "id": "IGAGGIAN3",
    "lat": "45.40463638",
    "lon": "9.03504276"
}, {"id": "IMILAN148", "lat": "45.50156021", "lon": "9.16270828"}, {
    "id": "IMILANO314",
    "lat": "45.47852707",
    "lon": "9.11737537"
}, {"id": "IMILANO241", "lat": "45.42798233", "lon": "9.20416164"}, {
    "id": "IBOLLATE9",
    "lat": "45.54544830",
    "lon": "9.11831665"
}, {"id": "ILMSANTA16", "lat": "45.47006607", "lon": "9.18354511"}, {
    "id": "ILMMILLE5",
    "lat": "45.44945526",
    "lon": "9.22226715"
}, {"id": "IMILANO392", "lat": "45.44628143", "lon": "9.16393089"}, {
    "id": "IMILAN155",
    "lat": "45.50701141",
    "lon": "9.12349796"
}, {"id": "IMILANO515", "lat": "45.48032379", "lon": "9.24929428"}, {
    "id": "IMILANO270",
    "lat": "45.44279480",
    "lon": "9.26392460"
}, {"id": "ILMCRESC7", "lat": "45.51267242", "lon": "9.25539684"}, {
    "id": "IMILANO545",
    "lat": "45.44602966",
    "lon": "9.24815273"
}, {"id": "IMILAN106", "lat": "45.44240570", "lon": "9.20870304"}, {
    "id": "ILMCENTR4",
    "lat": "45.48010635",
    "lon": "9.19287205"
}, {"id": "ILMORTIC2", "lat": "45.47100449", "lon": "9.23645115"}, {
    "id": "ILMBOFFA2",
    "lat": "45.41966629",
    "lon": "9.17926598"
}, {"id": "ILMSEGUR3", "lat": "45.47369385", "lon": "9.06515694"}, {
    "id": "ILMSESTO4",
    "lat": "45.53092575",
    "lon": "9.23419571"
}, {"id": "IPOASCO2", "lat": "45.40059280", "lon": "9.23313713"}, {
    "id": "INOVIGLI2",
    "lat": "45.38083267",
    "lon": "9.09605789"
}, {"id": "ISANDONA17", "lat": "45.42143631", "lon": "9.26057529"}, {
    "id": "IMILAN124",
    "lat": "45.43049622",
    "lon": "9.05527687"
}, {"id": "IGAGGIAN5", "lat": "45.40858459", "lon": "9.05232334"}, {
    "id": "IROZZANO7",
    "lat": "45.38031006",
    "lon": "9.16498089"
}, {"id": "ILMCESAN3", "lat": "45.44134521", "lon": "9.08854961"}, {
    "id": "ISANGIUL23",
    "lat": "45.37821579",
    "lon": "9.26525497"
}, {"id": "IMILANO676", "lat": "45.41416550", "lon": "9.13629627"}, {
    "id": "IBUCCINA11",
    "lat": "45.40501785",
    "lon": "9.12115097"
}, {"id": "ILMFIERA5", "lat": "45.48067093", "lon": "9.14587402"}, {
    "id": "IASSAGO2",
    "lat": "45.40922928",
    "lon": "9.15412998"
}, {"id": "IROZZANO2", "lat": "45.40474701", "lon": "9.17123127"}];

//Function to query WunderAPI inserting the available stations and their position
var requests = [];
requests[stationIndex] = [];
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
                if (indexDay < 1) { //Query only X days (1 now)
                    indexDay++;
                    sleep(10000); // sleep for ten seconds (rate limit 10 calls per minute)
                    query();
                } else if (stationIndex < stations.length) {
                    indexDay = 1;
                    save(csv, station);
                    csv = [];
                    InitDate = new Date("01/01/2016");
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