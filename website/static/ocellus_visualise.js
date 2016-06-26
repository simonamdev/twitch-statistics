// Reference used:
// https://stackoverflow.com/questions/2190801/passing-parameters-to-javascript-files

var OCELLUS_VISUALISE = OCELLUS_VISUALISE || (function(){
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
						        // Get a container to show the visualisation in
				            var container = document.getElementById("visualisation-viewers");
                    console.log("Created container");
				            jsonData = JSON.parse(data);
				            console.log("Parsing data");
										// Create a new dataset with the received data
										var dataset = new vis.DataSet(jsonData);
										console.log("Created dataset");
										// Set some options
										console.log("Setting options");
										var options = {
												drawPoints: false,
												dataAxis: {
														'left': {
																'title': {
																		'text': 'Viewers'
																}
														}
												}
										}
										console.log("Displaying graph");
										// Create the graph and display it
										var graph2d = new vis.Graph2d(container, dataset, options);
						    }
						});
        },
        visualiseStreamerAverageViewers: function() {
            console.log("Visualising average viewers for " + _args[0] + "'s " + _args[1]);
            // Make an AJAX call to get the data
            $.ajax({
						    url: "/api/v1/streamer/" + _args[0] + "/" + _args[1],
						    success: function(data){
						        console.log("Received data");
						        console.log(data);
						        // Get a container to show the visualisation in
						        /*
				            var container = document.getElementById("ED-average-viewers-graph");
                    console.log("Created container");
				            jsonData = JSON.parse(data);
				            console.log(jsonData);
				            */
				            /*
				            console.log("Parsing data");
										// Create a new dataset with the received data
										var dataset = new vis.DataSet(jsonData);
										console.log("Created dataset");
										// Set some options
										console.log("Setting options");
										var options = {
												drawPoints: false,
												dataAxis: {
														'left': {
																'title': {
																		'text': 'Viewers'
																}
														}
												}
										}
										console.log("Displaying graph");
										// Create the graph and display it
										var graph2d = new vis.Graph2d(container, dataset, options);
										*/
						    }
						});
        }
    };
}());
