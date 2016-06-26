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
				            jsonData.forEach(function(point) {
				                timeStamps.push(String(point['x']));
				                dataPoints.push(parseInt(point['y']));
				            });

	                  var lineChartData = {
	                      labels: timeStamps,
	                      datasets: [
	                          {
	                              strokeColor: "rgba(220,220,220,1)",
	                              data: dataPoints
	                          }
	                      ]
	                  }

										var ctx = document.getElementById("visualisation-viewers").getContext("2d");
										var myLineChart = new Chart(ctx, {
												type: 'line',
												data: lineChartData
										});
/*
						        var myChart = new Chart(ctx, {
						            type: 'line',
						            //data: data,
						            options: {
						                scales: {
						                    xAxes: [{
						                        type: 'linear',
						                        position: 'bottom'
						                    }]
						                }
						            }
						        });
						        */
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
