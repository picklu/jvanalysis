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
            $rowTable.html(`<td><input id="data-${i}" type="button" class="btn btn-sm my-sm-0 btn-primary editable" value="Edit"></td>`);
            $(row).each((j, col) => {
                $rowTable.append(`<td><span class="data-${i}">${col}</span></td>`);
            });
            $dt.append($rowTable);
        });
        toggleEdit();
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

function toggleEdit() {
    $('td input[type="button"]').on("click", (event) => {
        var $this = $(event.currentTarget);
        var $dataSpan = $(`.${$this.prop('id')}`);
        
        if ($this.val() == 'Edit') {
            $this.val('Done')
                 .addClass('btn-info')
                 .removeClass('btn-primary');
            $dataSpan.attr('contenteditable', true)
                     .addClass('lead');
        }
        else {
            $this.val('Edit')
                 .addClass('btn-primary')
                 .removeClass('btn-info');
            $dataSpan.attr('contenteditable', false)
                     .removeClass('lead');
        }
    });
}