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
        
        // show ajax-loader
        $('#table-container').html(getAjaxLoader());
        
        // read file, save rawData, and parse the rawData
        reader.onload = function() {
            var delimiter = $('#delimiter').val();
            rawData = this.result;
            parseData(rawData, delimiter);
        };
        reader.readAsText(file);
    }
}

/*********************************
* Return a div with class table-data
* and image ajax laoder gif file
* triggered when a file is slected
**********************************/
function getAjaxLoader() {
    var $ajaxLoader = $('<div/>', {
        class: 'table-data ajax-loader-container',
        html: $('<img/>', {
            class: 'ajax-loader',
            alt: 'loading file',
            src: Flask.url_for('static', {'filename': 'images/ajax-loader.gif'})
        })
    });
    
    return $ajaxLoader;
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
    var alertType = showData(parsedData);
    var message;
    if (alertType == 'success') {
        message = getDataInfo();
    }
    else if (alertType == 'fail') {
        message = 'There is no data!';
    }
    alertTable(message, alertType);
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

/**********************************
* Create table when file is loaded 
* for the first time
* invoked from showData
***********************************/
function createTable() {
    var $tHead = $('<thead/>');
    var $tBody = $('<tbody/>');
    var $table = $('<table/>', {
            id: 'raw-data',
            class: 'table table-bordered'
        });
    var $tableDiv = $('<div/>', {
        class: 'table-data',
        html: $table
    });
    
    // append thead and tbody to the table
    $table.append($tHead).append($tBody);
    
        
    // add table to table container
    $('#table-container').html($tableDiv);
    
    return {
        thead: $tHead, 
        tbody: $tBody
    };
}

/**********************************
* Create table header for row
* invoked from showData
***********************************/
function createTableHeader(row) {
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
    $(row).each(function(i, col) {
        var $tHeader = $('<th/>');
        var $tSelect = $('<select/>', {
            id: 'cv' + i,
            class: 'form-control text-capitalize',
            name: 'cv' + i
        });
        $(options).each(function(j, opt) {
            var $selectOption = $('<option/>', {
                name:'cv' + i,
                value: opt,
                selected: (i == j),
                text: opt
            });
            $tSelect.append($selectOption);
        });
        $tHeader.append($tSelect).appendTo($tableHeader);
    });
    
    return $tableHeader;
}

/************************************
* Create table row with the data row 
* invoked from showData
*************************************/
function createTableRow(row, idx) {
    var $tableRow = $('<tr/>', {
        row: idx
    });
    
    // button for each row
    $('<td/>', {
        class: 'table-fit',
        html: $('<button/>', {
            class: 'row-crossout btn btn-xs btn-warning',
            text: '\u274C'
        })
    }).append('&nbsp;').append($('<input/>', {
        type: 'button', 
        class: 'btn btn-xs btn-info',
        value: '\u270D'
        })
    ).appendTo($tableRow);
    
    // data for each row
    $(row).each(function(i, col) {
        $('<td/>', {
            row: idx,
            col: i,
            html: $('<span/>', {
                class: 'data-cell',
                text: (col == '') ? 'NaN' : col
            })
        }).append($('<span/>', {
            text: '\xa0\xa0'
        })).append($('<button/>', {
            class: 'cell-crossout btn btn-xs',
            text: '\u274C'
        })).appendTo($tableRow);
    });
    
    return $tableRow;
}

/**************************
* Display data in a table
* invoked from parseData
***************************/
function showData(data) {
    if (data.length) {
        // if there is data in the data
        var $table = createTable();
        
        $(data).each(function(i, row) {
            // create table header //
            if (i == 0) {
                var $tableHeader = createTableHeader(row);
                $table.thead.append($tableHeader);
            }
            // create table body //
            var $tableBodyRow = createTableRow(row, i);
            $table.tbody.append($tableBodyRow);
        });
         
        // invoke event handlers for table
        deleteRow();
        deleteCell();
        toggleEdit();
        headerAction();
        toggleSelection();
        getDataInfo();
        
        return 'success';
    }
    else {
        // there was no data
        $('#table-container').html(null);
        
        return 'fail';
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
    $('td input[type=button]').on('click', function() {
        var $this = $(this);
        var $dataSpan = $this.parents(':eq(1)').find('span.data-cell');
        
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
* Delete a cell in the data table
* invoked from showData
***********************************/
function deleteCell() {
    $('.cell-crossout').on('click', function() {
        var $cell = $(this).parent();
        var rowIndex = $cell.attr('row');
        var colIndex = $cell.attr('col');
        var message;
        
        // update parsed data 
        parsedData[rowIndex].splice(colIndex, 1);
        
        // remove the cell
        $cell.remove();
        
        // display message
        message = getDataInfo();
        message = 'Table cell at row ' + rowIndex + ' and col ' + 
            colIndex + ' has been deleted!. ' + message;
        alertTable(message, 'warning');
    });
}

/**********************************
* Delete a row in the data table
* invoked from showData
***********************************/
function deleteRow() {
    $('.row-crossout').on('click', function() {
        var message;
        var $row = $(this).parents(':eq(1)');
        var rowIndex = $row.attr('row');
        
        // update parsed data
        parsedData.splice(rowIndex, 1);
        
        // remove the row
        $row.remove();
        
        // show data in a table
        var alertType = showData(parsedData);
        
        if (alertType == 'success') {
            message = getDataInfo();
            message = 'Table row at ' + rowIndex + ' has been deleted! ' + message;
            alertType = 'warning';
        }
        else if (alertType == 'fail') {
            message = 'There is no data!';
        }
        
        alertTable(message, alertType);
        
    });
}

/**********************************
* Triggered by mouse over/out
* invoked from showData
***********************************/
function headerAction() {
    $('th.table-fit span').hover(function() {
        var $this = $(this);
        var $dataSelect = $this.parents(':eq(1)').find('select');
        $this.addClass('text-uppercase');
        $dataSelect.addClass('font-weight-bold');
    }, function() {
        var $this = $(this);
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
    
    $('th select').on('focus', function() {
        previous = $(this).val();
    }).change(function() {
        var $this = $(this);
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
function getDataInfo() {
    var numRws = parsedData.length;
    var numCols = parsedData[0].length;
    
    return 'There are total ' + numRws + 
        ' row(s) and '+ numCols + 
        ' column(s) (based on first row) in the data.';
}

/**********************************
* Show alert message for the data table
* invoked from showData
***********************************/
function alertTable(message, alertType) {
    // create div for data info inside info container
    var $alertDiv = $('<div/>', {
        class: 'alert',
        html: $('<span/>', {
            id: 'data-info'
        })
    });
    
    if (alertType == 'success') {
        // create show/hide button
        var $tableShowHide = $('<strong/>', {
                    id: 'table-show-hide',
                    text: 'Hide table'
        });
        
        // add appropriate class and add the show/hide button 
        $alertDiv.addClass('alert-info')
                 .append('&nbsp;').append($tableShowHide);
        
        // hover and click event handler for show/hide
        $tableShowHide.hover(function() {
            $(this).addClass('text-success');
        }, function() {
            var $this = $(this);
            $(this).removeClass('text-success');
        }).on('click', function() {
            var $this = $(this);
            var $tableContainer = $('#table-container');
            
            if ($this.text() == 'Hide table') {
                $this.text('Show table');
                $tableContainer.hide();
            }
            else {
                $this.text('Hide table');
                $tableContainer.show();
            }
        });
        
    }
    else if (alertType == 'warning') {
        // add appropriate class
        $alertDiv.addClass('alert-warning');
    }
    else if (alertType == 'fail') {
        // add appropriate class
        $alertDiv.addClass('alert-danger');
    }
    
    // set the html of the table info container
    $alertDiv.find('span').text(message);
    $('#table-info-container').html($alertDiv);
}