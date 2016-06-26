// Reference used:
// https://stackoverflow.com/questions/2190801/passing-parameters-to-javascript-files

var OCELLUS_CHARTS = OCELLUS_CHARTS || (function(){
    var _args = {}; // private

    return {
        initForStream : function(Args) {
            _args = Args;
        },
        initForStreamer : function(Args) {
            _args = Args;
        },
        displayStreamArguments : function() {
            alert('Streamer Name: ' + _args[0] + '\nGame shorthand name: ' + _args[1] + '\nStream ID: ' + _args[2]);
        },
        displayStreamerArguments : function() {
            alert('Streamer Name: ' + _args[0] + '\nGame shorthand name: ' + _args[1]);
        },
        visualiseStreamViewers: function() {
            console.log("Visualising viewers for " + _args[0] + "'s " + _args[1] + " #" + _args[2] + " stream.");
            // Make an AJAX call to get the data
            $.ajax({
						    url: "/api/v1/raw_stream_data/" + _args[0] + "/" + _args[1] + "/" + _args[2],
						    success: function(data){
						        console.log("Received data");
				            jsonData = JSON.parse(data);
				            var timeStamps = [];
				            var dataPoints = [];

										console.log("Parsing data");
				            jsonData.forEach(function(point) {
				                timeStamps.push(String(point['time']));
				                dataPoints.push(parseInt(point['viewers']));
				            });

										console.log("Forming chart data");
	                  var lineChartData = {
	                      labels: timeStamps,
	                      datasets: [
	                          {
	                              label: "Viewers",
	                              borderColor: "rgba(0,0,255,1)",
	                              strokeColor: "rgba(0,0,255,1)",
	                              lineTension: 0.1,
	                              pointRadius: 0,
	                              borderWidth: 3,
	                              fill: false,
	                              data: dataPoints
	                          }
	                      ]
	                  }

										console.log("Drawing chart");
										var ctx = document.getElementById("visualisation-viewers").getContext("2d");
										var myLineChart = new Chart(ctx, {
												type: 'line',
												data: lineChartData,
												options: {
														height: '100%',
														responsive: true,
														title: {
																display: true,
																text: "Viewers over time"
														}
												}
										});
						    }
						});
        },
        visualiseStreamerAverageViewers: function() {
            console.log("Visualising average viewers for " + _args[0] + "'s " + _args[1]);
            // Make an AJAX call to get the data
            $.ajax({
						    url: "/api/v1/streamer/" + _args[0] + "/" + _args[1],
						    success: function(data){

				            jsonData = JSON.parse(data);
				            console.log("Parsing data");

						    }
						});
        }
    };
}());
