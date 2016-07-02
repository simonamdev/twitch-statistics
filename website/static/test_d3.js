d3.request("/api/v1/streamer/gophergaming", function(apiData) {
		jsondata = JSON.parse(apiData.responseText);
		console.log(jsondata);
});