/* Callback Function for Nearby Places */
function callback(data) {
  console.log(data);
}

/* Function to get Nearby Places */
function getNearbyPlaces(id) {
  let to_id = id;
  to = $("#" + to_id).val();
  if (to != "") {
    /*Nearby plugin initialization*/
    map = new mappls.Map("map", {
      center: { lat: 28.612964, lng: 77.229463 },
      zoom: 9,
    });
    var options = {
      map: map,
      //divId: "nearby_search",
      keywords: "restaurants",
      refLocation: [28.632735, 77.219696],
      //refLocation: [to_eloc],
      fitbounds: true,
      geolocation: true,
      click_callback: function (d) {
        console.log(d);
      },
    };

    //mappls.nearby(options, callback); //Function Call
  }
}

/* Functionto Calculate Distance between two places */
function calculateDistance(from, to) {
  var distance = 0;
  var locs = from + ";" + to;
  mappls.getDistance(
    {
      //Kodur, Rajampet Distance (44173: By API)  (45km by Google Maps) (44173m : 44km )
      coordinates: "", //"13.9553622,79.3397819;14.1937301,79.1360947",
    },
    function (data) {
      distance = data.results.distances[0][1];
      console.log(data);
    }
  );
  setTimeout(() => {
    console.log(distance);
  }, 500);
  return distance;
}

/* Function to get Text Suggestions */
var from_eloc = "";
var to_eloc = "";
function initMap1() {
  if (!document.getElementById("from").classList.contains("select")) {
    new mappls.search(document.getElementById("from"), callback_from);
  }
  if (!document.getElementById("to").classList.contains("select")) {
    new mappls.search(document.getElementById("to"), callback_to);
  }
  function callback_from(data) {
    if (data) {
      var dt = data[0];
      var placeName = dt["placeName"];
      from_eloc = dt["eLoc"];
      if (placeName == "Current Location") {
        var lat = dt["latitude"];
        var lon = dt["longitude"];
        var res = fetch(
          "https://apis.mapmyindia.com/advancedmaps/v1/37a02b3ee6abf2878ef11efc92c43c09/rev_geocode?lat=" +
            lat +
            "&lng=" +
            lon
        )
          .then((res_data) => {
            jsonData = res_data.text();
            return jsonData;
          })
          .then((jsonData) => {
            obj = JSON.parse(jsonData);
            placeName =
              obj.results[0].subLocality + ", " + obj.results[0].locality;
            document.querySelector("#from").value = placeName;
          });
      } else {
        document.querySelector("#from").value = placeName;
      }
      if (!dt) return false;
      var eloc = dt.eLoc;
      var place = dt.placeName;
    }
  }

  function callback_to(data) {
    if (data) {
      var dt = data[0];
      var placeName = dt["placeName"];
      to_eloc = dt["eLoc"];
      if (placeName == "Current Location") {
        var lat = dt["latitude"];
        var lon = dt["longitude"];
        var res = fetch(
          "https://apis.mapmyindia.com/advancedmaps/v1/37a02b3ee6abf2878ef11efc92c43c09/rev_geocode?lat=" +
            lat +
            "&lng=" +
            lon
        )
          .then((res_data) => {
            jsonData = res_data.text();
            return jsonData;
          })
          .then((jsonData) => {
            obj = JSON.parse(jsonData);
            placeName =
              obj.results[0].subLocality + ", " + obj.results[0].locality;
            document.querySelector("#to").value = placeName;
          });
      } else {
        document.querySelector("#to").value = placeName;
      }
      if (!dt) return false;
      var eloc = dt.eLoc;
      var place = dt.placeName;
    }
  }
}
