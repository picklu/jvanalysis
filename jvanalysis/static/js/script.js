var rawData;
var parsedData;

function uploadFile() {
    var fileObject = $('#data-file').prop('files');
    if (fileObject.length) {
        var file = fileObject[0];
        var reader = new FileReader();
        // update file control text area
        $('.custom-file-control').text(file.name);
        reader.onload = function(e) {
            var delimiter = $('#delimiter').val();
            rawData = e.target.result;
            parseDataFile(rawData, delimiter);
        };
        reader.readAsText(file);
    }
}

function parseDataFile(csvData, delimiter) {
    var config = {delimiter: ''};
    switch(delimiter) {
        case 'tab':
            config.delimiter = '\t';
            break;
        case 'space':
            config.delimiter = ' ';
            break;
        case 'comma':
            config.delimiter = ',';
            break;
        case 'semicolon':
            config.delimiter = ';';
            break;
    }
    parsedData = Papa.parse(csvData, config).data;
    showData(parsedData);
}

function reParse() {
    var fileObject = $('#data-file').prop('files');
    if (fileObject.length && rawData) {
        var delimiter = $('#delimiter').val();
        parseDataFile(rawData, delimiter);
    }
}

function showData(data) {
    var $dt = $('#raw-data');
    $dt.html('Loading data ...');
    if (data.length) {
        $dt.html(null);
        $(data).each(function(i, row) {
            if (i == 0) {
                var $rowTable = $('<tr/>');
                var availableOptions = ["voltage", "current", "unknown", "unknonw1","unknonw2"];
                var options = availableOptions.slice(0, row.length);
                $rowTable.html('<th class="table-fit"><span class="form-control">Header</span></th>');
                $(row).each(function(j, col) {
                    var $tHeader = $('<th/>');
                    var $tSelect = $(`<select id="cv${j}" class="form-control text-capitalize" name="cv${j}"></select>`);
                    $(options).each(function(k, opt) {
                        var selected = (j == k) ? "selected" : "";
                        $tSelect.append(`<option name="cv${j}" value="${opt}" ${selected}>${opt}</option>`);
                    });
                    $tHeader.append($tSelect);
                    $rowTable.append($tHeader);
                });
                $dt.append($rowTable);
            }
            var $rowTable = $('<tr/>');
            $rowTable.html(`<td class="table-fit"><button class="btn btn-sm my-sm-0 btn-warning">&#x274c;</button>&nbsp;<input id="data-${i}" type="button" class="btn btn-sm my-sm-0 btn-info" value="&#x270D;"></td>`);
            $(row).each(function(l, col) {
                $rowTable.append(`<td><span>${col}</span></td>`);
            });
            $dt.append($rowTable);
        });
        deleteRow();
        toggleEdit();
        headerAction();
        toggleSelection();
        updateDataInfo();
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
    $('td input[type="button"]').on("click", function(event) {
        var $this = $(event.currentTarget);
        var $dataSpan = $this.parents(':eq(1)').find('span');
        
        if ($this.val() == '\u270D') {
            $this.val('	\u2714');
            $dataSpan.attr('contenteditable', true)
                     .addClass('lead');
        }
        else {
            $this.val('\u270D');
            $dataSpan.attr('contenteditable', false)
                     .removeClass('lead');
        }
    });
}

function deleteRow() {
    $('td button').on("click", function(event) {
        var $this = $(event.currentTarget);
        $this.parents(':eq(1)').remove();
        updateDataInfo();
    });
}

function headerAction() {
    $('th.table-fit span').hover(function(event) {
        var $this = $(event.currentTarget);
        var $dataSelect = $this.parents(':eq(1)').find('select');
        $this.addClass('text-uppercase');
        $dataSelect.addClass('font-weight-bold');
    }, function(event) {
        var $this = $(event.currentTarget);
        var $dataSelect = $this.parents(':eq(1)').find('select');
        $this.removeClass('text-uppercase');
        $dataSelect.removeClass('font-weight-bold'); 
    });
}

function toggleSelection() {
    var previous;
    $('th select').on('focus', function(e) {
        previous = $(e.target).val();
    }).change(function(e) {
        var $this = $(e.target);
        var current = $this.val();
        $('th select').each(function(i, sl) {
          if ($this.attr('id') != $(sl).attr('id') && 
            current == $(sl).val()) {
              $(sl).val(previous);
              previous = current;
          }
        });
    });
}

function updateDataInfo() {
    var numRws = $('#raw-data').find('tr').length - 1;
    var numCols = $('#raw-data').find('th').length - 1;
    $('#data-info').text(`${numRws} row(s) and ${numCols} header column(s)`);
}