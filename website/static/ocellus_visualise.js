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
            alert('Streamer Name: ' + _args[0]);
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
        visualiseStreamerData: function() {
            console.log("Visualising viewers/followers for " + _args[0]);
            // Make an AJAX call to get the data
            $.ajax({
						    url: "/api/v1/streamer/" + _args[0],
						    success: function(data) {
						        console.log("Received data");
				            jsonData = JSON.parse(data);
										console.log("Parsing data for each game");
										$.each(jsonData, function(key, value) {
													console.log("Parsing data for: " + key);
													if ($.isEmptyObject(value)) {
															console.log("Streamer has no data for: " + key);
													} else {
															console.log("Data for: " + key);
															console.log(value);

															var viewersData = {"time": [], "value": []};
									            value["viewers_average"].forEach(function(point) {
									                viewersData["time"].push(String(point["time"]));
									                viewersData["value"].push(parseInt(point["value"]));
									            });

									            var followersData = {"time": [], "value": []};
															console.log("Parsing followers data");
									            value["followers"].forEach(function(point) {
									                followersData["time"].push(String(point["time"]));
									                followersData["value"].push(parseInt(point["value"]));
									            });

									            console.log("Forming viewers chart data");

									            var viewersLineChartData = {
						                      labels: viewersData["time"],
						                      datasets: [
						                          {
						                              label: "Average Viewers",
						                              borderColor: "rgba(0,0,255,1)",
						                              strokeColor: "rgba(0,0,255,1)",
						                              lineTension: 0.1,
						                              pointRadius: 0,
						                              borderWidth: 3,
						                              fill: false,
						                              data: viewersData["value"]
						                          }
						                      ]
						                  }

						                  console.log("Forming followers chart data");
						                  var followersLineChartData = {
						                      labels: followersData["time"],
						                      datasets: [
						                          {
						                              label: "Followers",
						                              borderColor: "rgba(0,0,255,1)",
						                              strokeColor: "rgba(0,0,255,1)",
						                              lineTension: 0.1,
						                              pointRadius: 0,
						                              borderWidth: 3,
						                              fill: false,
						                              data: followersData["value"]
						                          }
						                      ]
						                  }

															console.log("Drawing charts");

															var graph = key + "-average-viewers-graph";
															var ctx = document.getElementById(graph).getContext("2d");
															var viewersLineChart = new Chart(ctx, {
																	type: 'line',
																	data: viewersLineChartData,
																	options: {
																			height: '100%',
																			responsive: true,
																			title: {
																					display: true,
																					text: "Average Viewers over time"
																			}
																	}
															});
															var graph = key + "-followers-graph";
															ctx = document.getElementById(graph).getContext("2d");
															var followersLineChart = new Chart(ctx, {
																	type: 'line',
																	data: followersLineChartData,
																	options: {
																			height: '100%',
																			responsive: true,
																			title: {
																					display: true,
																					text: "Followers over time"
																			}
																	}
															});
													}
										});
						    }
						});
        }
    };
}());
