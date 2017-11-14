function readTextFile() {
    $('input[type=file]').parse({
    	config: {
    		complete: (results, file) => {
    		    saveLocal(file, results.data);
    			showData(results.data);
    		}
    	},
    	complete: () => {
    		console.log('Done!');
    	}
    });
}

function showData(data) {
    var $dt = $('#raw-data');
    $dt.html('Loading data ...');
    if (data.length) {
        $dt.html(null);
        $(data).each((i, row) => {
            var $rowTable = $('<tr/>');
            $rowTable.html(`<th><input id="dt${i}" type="checkbox"> ${i+1}</th>`);
            $(row).each((j, col) => {
                $rowTable.append(`<td>${col}</td>`);
            });
            $dt.append($rowTable);
        });
    }
    else {
        $dt.html('No data found!');
    }
}

function saveLocal(file, data) {
    localStorage.setItem('file', JSON.stringify({
        fname: file.name,
        fSize: file.size,
        data: data
    }));
}