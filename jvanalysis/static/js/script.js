/*********************************
* Global variables
**********************************/
var rawData;
var parsedData;
var isTableVisible = false;

/*********************************
* Upload text or csv file
* triggered when a file is slected
**********************************/
function uploadFile() {
    // empty table container
    $('#table-container').html(null);
    
    // set table visibility to false
    isTableVisible = false;
    
    var fileObject = $('#data-file').prop('files');
    
    if (fileObject.length) {
        var file = fileObject[0];
        var reader = new FileReader();
        
        // update file control text area
        $('.custom-file-control').text(file.name);
        
        // read file, save rawData, and parse the rawData
        reader.onload = function() {
            var delimiter = $('#delimiter').val();
            rawData = this.result;
            parseData(rawData, delimiter);
        };
        reader.readAsText(file);
    }
    else{
        rawData = "";
        parsedData = [];
        // update file control text area and alert box
        message = 'No file was selected!';
        alertTable(message, 'fail');
        $('.custom-file-control').text('Choose file ...');
    }
}

/*********************************
* Return a div with class table-data
* and image ajax laoder gif file
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
    
    // show table data info
    var alertType = parsedData.length ? 'success' : 'fail';
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
    // empty table container
    $('#table-container').html(null);
    
    // If there is already a data then reparse
    var fileObject = $('#data-file').prop('files');
    if (fileObject.length && rawData.length) {
        var delimiter = $('#delimiter').val();
        parseData(rawData, delimiter);
        if (isTableVisible) {
            showData(parsedData);
        }
    }
}

/*******************************************
* Create a table element inside a div 
* return an object containing thead and tbody
* invoked from showData
********************************************/
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
    
    return {
        tmain: $tableDiv,
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
            col: i,
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

/********************************************************
* Display data in a table
* invoked from reParseData, deleteRow, and tableShowHide
*********************************************************/
function showData(data) {
    var $tableContainer = $('#table-container');
    var $table = createTable();
    var $ajaxLoader = getAjaxLoader();
    
    // show ajax loader
    $tableContainer.html($ajaxLoader);
    
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
    
    // place table in the table container
    $tableContainer.html($table.tmain);
     
    // invoke event handlers for table
    deleteRow();
    deleteCell();
    toggleEdit();
    headerAction();
    toggleSelection();
    getDataInfo();
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
            colIndex + ' has been deleted! ' + message;
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
        
        var alertType = parsedData.length ? 'success' : 'fail';
        
        if (alertType == 'success') {
            showData(parsedData); 
            message = getDataInfo();
            message = 'Table row at ' + rowIndex + ' has been deleted! ' + message;
            alertType = 'warning';
        }
        else if (alertType == 'fail') {
            $('#table-container').html(null);
            message = 'There is no data in the table!';
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
    var numCols = numRws ? parsedData[0].length : 0;
    
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
    var $alertInfo = $('<span/>', {
        id: 'alert-message'
    });
    var $alertDivInfo = $('<span/>', {
        id: 'alert-info-container',
        html: $alertInfo
    });
    var $alertType = $('<h5/>', {
        id: 'alert-type'
    });
    var $alertDiv = $('<div/>', {
        id: 'alert-table',
        class: 'alert alert-dismissible fade show',
        role: 'alert',
        html: $alertType
    });
    
    $alertDiv.append($alertDivInfo);
    
    // create alert close button
    var $buttonClose = alertClose();
    $alertDiv.prepend($buttonClose);
    
    if (alertType == 'fail') {
        // show alert type
        $alertType.text('Fail:');
        
        // add appropriate class
        $alertDiv.addClass('alert-danger');
    }
    else {
        // create table show/hide button
        var $buttonShowHide = tableShowHide();
        $alertDivInfo.append($('<span/>', {
            text: '\xa0\xa0'
        })).append($buttonShowHide);
        
        
        if (alertType == 'success') {
            // show alert type
            $alertType.text('Success:');
        
            // add appropriate class and add the show/hide button 
            $alertDiv.addClass('alert-info');
            
            // update visibility of close button
            if (!isTableVisible) {
                $buttonClose.hide();
            }
        }
        else if (alertType == 'warning') {
            // show alert type
            $alertType.text('Warning:');
            
            // add appropriate class
            $alertDiv.addClass('alert-warning');
        }
    }
    
    // set the html of the table info container
    $alertDiv.find('#alert-message').text(message);
    $('#table-info-container').html($alertDiv);
}

/**********************************
* Create table show/hide button
* invoked from alertTable
***********************************/
function tableShowHide() {
    // create show/hide button
    var $buttonShowHide = $('<strong/>', {
        id: 'table-show-hide',
        text: isTableVisible ? 'Hide table' : 'Show table'
    });
    
    // hover and click event handler for show/hide
    $buttonShowHide.hover(function() {
        $(this).addClass('text-success');
    }, function() {
        $(this).removeClass('text-success');
    }).on('click', function() {
        var $this = $(this);
        var $buttonClose = $('#alert-close');
        var $alertDiv = $('#alert-table');
        var $tableContainer = $('#table-container');
        
        // update alert div text
        $alertDiv.find('#alert-type').text('');
        $alertDiv.find('#alert-message').text('');
        
        // update alert class
        if (!$alertDiv.hasClass('info')) {
            $alertDiv.removeClass('alert-danger')
                     .removeClass('alert-warning')
                     .addClass('alert-info');
        }
        
        // update visibility and button text
        if (isTableVisible) {
            isTableVisible = false;
            $this.text('Show table');
            $tableContainer.hide(500);
            $buttonClose.hide();
        }
        else {
            isTableVisible = true;
            $this.text('Hide table');
            $buttonClose.show();
            if (!$('#raw-data').length) {
                showData(parsedData);
            }
            $tableContainer.show();
            
        }
    });
    
    return $buttonShowHide;
}

/**********************************
* Create alert hide button
* invoked from alertTable
***********************************/
function alertClose() {
    var $buttonClose = $('<button/>', {
        id: 'alert-close',
        type: 'button',
        class: 'close',
        'data-dismiss': 'alert',
        'aria-label': 'Close',
        html: $('<span/>', {
            'aria-hidden': 'true',
            text: '\u274C'
        })
    });
            
    return $buttonClose;
}
