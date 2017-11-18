var rawData;
var parsedData;

/*********************************
* Upload text or csv file
* triggered when a file is slected
**********************************/
function uploadFile() {
    var fileObject = $('#data-file').prop('files');
    
    if (fileObject.length) {
        var file = fileObject[0];
        var reader = new FileReader();
        
        // update file control text area
        $('.custom-file-control').text(file.name);
        
        // read file, save rawData, and parse the rawData
        reader.onload = function(e) {
            var delimiter = $('#delimiter').val();
            rawData = e.target.result;
            parseData(rawData, delimiter);
        };
        reader.readAsText(file);
    }
}

/**********************************
* Parse csv data with Papa parse
***********************************/
function parseData(csvData, delimiter) {
    var config = {delimiter: ''};
    
    // re configure according to delimiter
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
    
    // parse data with Papa parse
    parsedData = Papa.parse(csvData, config).data;
    
    // show data in a table
    showData(parsedData);
}

/**********************************
* Reparse csv data with parseData
* triggered when delimiter is changed
***********************************/
function reParseData() {
    var fileObject = $('#data-file').prop('files');
    if (fileObject.length && rawData) {
        var delimiter = $('#delimiter').val();
        parseData(rawData, delimiter);
    }
}

/**************************
* Display data in a table
* invoked from parseData
***************************/
function showData(data) {
    var $rowDataTable = $('#row-table-data');
    var $dataTable = $('<table/>', {
        id: 'raw-data',
        class: 'table table-bordered'
    });
    
    $rowDataTable.append($('<div/>', {
        class: 'row',
        html: $('<div/>', {
            class: 'col-md-12',
            html: $('<h5/>', {
                html: $('<span/>', {
                text: 'Data: '
            })
        }).append($('<span/>', {
                id: 'data-info'
            }))
        })
    }));
    
    $('<div/>', {
        class: 'row',
        html: $('<div/>', {
            class: 'col-md-12',
            html: $('<div/>', {
                class: 'table-data',
                html: $dataTable
            })
        })
    }).appendTo($rowDataTable);
    
    if (data.length) {
        // if there is data in the data
        // clear the data table
        $dataTable.html(null);
        $(data).each(function(i, row) {
            // create table header //
            if (i == 0) {
                var availableOptions = ["voltage", "current", "other", 
                        "other1", "other2", "other3", "other4", "other5"];
                var options = availableOptions.slice(0, row.length);
                var $tableHeader = $('<tr/>', {
                    html: $('<th/>', {
                        class: 'table-fit',
                        html: $('<span/>', {
                            class: 'form-control',
                            text: 'Header'
                        })
                    })
                });
                $(row).each(function(j, col) {
                    var $tHeader = $('<th/>');
                    var $tSelect = $('<select/>', {
                        id: 'cv' + j,
                        class: 'form-control text-capitalize',
                        name: 'cv' + j
                    });
                    $(options).each(function(k, opt) {
                        var $selectOption = $('<option/>', {
                            name:'cv' + j,
                            value: opt,
                            selected: (j == k),
                            text: opt
                        });
                        $tSelect.append($selectOption);
                    });
                    $tHeader.append($tSelect).appendTo($tableHeader);
                });
                $dataTable.append($tableHeader);
            }
            // create table body //
            var $rowTable = $('<tr/>');
            // buttons for each row
            $('<td/>', {
                class: 'table-fit',
                html: $('<button/>', {
                    class: 'btn btn-sm my-sm-0 btn-warning',
                    text: '\u274C'
                })
            }).append('&nbsp;').append($('<input/>', {
                id: 'data-' + i,
                type: 'button', 
                class: 'btn btn-sm my-sm-0 btn-info',
                value: '\u270D'
                })
            ).appendTo($rowTable);
            // data for each row
            $(row).each(function(l, col) {
                $('<td/>', {
                    html: $('<span/>', {
                        text: col
                    })
                }).appendTo($rowTable);
            });
            $dataTable.append($rowTable);
        });
        // invoke event handlers for table
        deleteRow();
        toggleEdit();
        headerAction();
        toggleSelection();
        updateDataInfo();
    }
    else {
        // there was no data
        $dataTable.html('No data found!');
    }
}

/**********************************
* Save data in localStorage
***********************************/
function saveLocal(file, data) {
    localStorage.setItem('file', JSON.stringify({
        fname: file.name,
        fSize: file.size,
        data: data
    }));
}

/**********************************
* Toggle edit button in data table
* invoked from showData
***********************************/
function toggleEdit() {
    $('td input[type="button"]').on("click", function(event) {
        var $this = $(event.currentTarget);
        var $dataSpan = $this.parents(':eq(1)').find('span');
        
        if ($this.val() == '\u270D') {
            $this.val('\u2714');
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

/**********************************
* Delete a row in the data table
* invoked from showData
***********************************/
function deleteRow() {
    $('td button').on("click", function(event) {
        var $this = $(event.currentTarget);
        $this.parents(':eq(1)').remove();
        updateDataInfo();
    });
}

/**********************************
* Triggered by mouse over/out
* invoked from showData
***********************************/
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

/**********************************
* Trigered by header selection change
* invoked from showData
***********************************/
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

/**********************************
* Show number of columns and rows in 
* the data table
* invoked from showData and deleteRow
***********************************/
function updateDataInfo() {
    var numRws = $('#raw-data').find('tr').length - 1;
    var numCols = $('#raw-data').find('th').length - 1;
    $('#data-info').text(numRws + ' row(s) and '+ numCols + ' header column(s)');
}