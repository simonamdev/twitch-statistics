// Reference used:
// https://stackoverflow.com/questions/2190801/passing-parameters-to-javascript-files

var OCELLUS_VISUALISE = OCELLUS_VISUALISE || (function(){
    var _args = {}; // private

    return {
        init : function(Args) {
            _args = Args;
        },
        displayArguments : function() {
            alert('Streamer Name: ' + _args[0] + '\nGame shorthand name: ' + _args[1] + '\nStream ID: ' + _args[2]);
        },
        visualiseViewers: function() {
            console.log("Visualising viewers for " + _args[0] + "'s " + _args[1] + " #" + _args[2] + " stream.");
            // Make an AJAX call to get the data
            $.ajax({
						    url: "/api/v1/raw_stream_data/" + _args[0] + "/" + _args[1] + "/" + _args[2],
						    success: function(data){
						        console.log(data);
						    }
						});
            // Get a container to show the visualisation in
            var container = document.getElementById('visualisation-viewers');


        }
    };
}());
/*
var container = document.getElementById('visualisation-viewers');
var items = [
    {x: '2014-06-11', y: 10},
    {x: '2014-06-12', y: 25},
    {x: '2014-06-13', y: 30},
    {x: '2014-06-14', y: 10},
    {x: '2014-06-15', y: 15},
    {x: '2014-06-16', y: 30}
];

var dataset = new vis.DataSet(items);
var options = {
    start: '2014-06-10',
    end: '2014-06-18'
};
var graph2d = new vis.Graph2d(container, dataset, options);
*/