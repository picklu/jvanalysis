/*********************************
* Global variables
**********************************/
var contentEditable = [];
var dataTableHeader = [];
var isTableVisible = true;
var jvData = {};

/*********************************
* Upload text or csv file
* triggered when a file is slected
**********************************/
function uploadFile() {
    var message;
    var alertType;
    var fileObject = $('#data-file').prop('files');
    var $tableContainer = $('#table-container');
    var $formAnalyze = $('#analyze');
    var $resultDiv = $('#results');
    
    // hide anlyze form
    if ($formAnalyze .attr('hidden') == 'hidden') {
        $formAnalyze .attr('hidden', false);
    }
    $formAnalyze .hide();
    
    // hide result button
    if ($resultDiv.attr('hidden') == 'hidden') {
        $resultDiv.attr('hidden', false);
    }
    $resultDiv.hide();
    
    // hide table container
    if ($tableContainer.attr('hidden') == 'hidden') {
        $tableContainer.attr('hidden', false);
    }
    $tableContainer.hide();
    isTableVisible = false;
    
    if (fileObject.length) {
        var file = fileObject[0];
        var fileName = file.name;

        if (file.size <= 10240) {
            var reader = new FileReader();
            // update file control text area
            $('.custom-file-control').text(fileName);
            
            // read file, save raw Data, and parse the raw data
            reader.onload = function() {
                var delimiter = $('#delimiter').val();
                jvData["raw"] = this.result;
                jvData["jv"] = parseData(jvData.raw, delimiter);
                // show table data info
                if (jvData.jv.length) {
                    jvData['name'] = fileName;
                    alertType = 'success';
                    message = getDataInfo();
                    $('#analyze').show();
                    // show ajax loader in the table container
                    $tableContainer.html(getAjaxLoader());
                    // show table
                    $tableContainer.show();
                    isTableVisible = true;
                    showData(jvData.jv);
                    alertTable(message, alertType, true);
                }
                else {
                    jvData = {};
                    alertType = 'fail';
                    message = 'There is no data!';
                    alertTable(message, alertType);
                }
            };
            reader.readAsText(file);
        }
        else {
            jvData = {};
            // update file control text area and alert box
            message = 'The size of the file "' + fileName + '" is larger than 10 kB!';
            alertTable(message, 'fail');
            // reset file object
            $('#data-file').val('');
            // update file control text area and alert box
            $('.custom-file-control').text('Choose file ...');
    }
    }
    else{
        jvData = {};
        // update file control text area and alert box
        message = 'No file was selected!';
        alertType = 'fail';
        alertTable(message, alertType);
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
    var data = Papa.parse(csvData, config).data;
    
    return data;
}

/**********************************
* Reparse csv data with parseData
* triggered when delimiter is changed
***********************************/
function reParseData() {
    var $tableContainer = $('#table-container');
    // empty table container
    $tableContainer.html(null);
    // If there is already a data then reparse
    var message;
    var alertType;
    var fileObject = $('#data-file').prop('files');
    if (fileObject.length && jvData.raw) {
        var delimiter = $('#delimiter').val();
        jvData.jv = parseData(jvData.raw, delimiter);
        // show table data info
        if (jvData.jv.length) {
            alertType = 'success';
            message = getDataInfo();
            $('#analyze').show();
            // show ajax loader in the table container
            if (isTableVisible) {
                $tableContainer.html(getAjaxLoader());
                showData(jvData.jv);
                alertTable(message, alertType, true);
                return false;
            }
        }
        else {
            jvData = {};
            alertType = 'fail';
            message = 'No data parsed!';
        }
    }
    else {
            jvData = {};
            alertType = 'fail';
            message = 'There is no data!';
    }
    alertTable(message, alertType);
    return false;
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
            class: 'table table-stripped'
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
                class: 'form-control no-border',
                text: '#'
            })
        })
    });
    $(row).each(function(i, col) {
        var $tHeader = $('<th/>');
        var $tSelect = $('<select/>', {
            col: i,
            class: 'form-control no-border text-capitalize',
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
        
        // populated dataTableHeader
        dataTableHeader.push(options[i]);
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
    $('<th/>', {
        class: 'table-fit',
        html: $('<span/>', {
            text: idx + 1
        })
    }).append($('<span/>', {
            class: 'row-crossout cursor-pointer',
            text: '\u274C'
        })).appendTo($tableRow);
    
    // data for each row
    $(row).each(function(i, col) {
        $('<td/>', {
            row: idx,
            col: i,
            html: $('<span/>', {
            class: 'cell-edit cursor-pointer',
            text: '\u270D'
            })
        }).append($('<span/>', {
            text: '\xa0\xa0'
            })
        ).append($('<span/>', {
                class: 'data-cell',
                text: (col == '') ? 'NaN' : col
            })
        ).append($('<span/>', {
            text: '\xa0\xa0'
            })
        ).append($('<span/>', {
            class: 'cell-crossout cursor-pointer',
            text: '\u274C'
            })
        ).appendTo($tableRow);
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
    $('#table-container').on('click', '.cell-edit', function() {
        var $this = $(this);
        var $dataContainer =  $this.parent();
        var row = $dataContainer.attr('row');
        var col = $dataContainer.attr('col');
        var $dataSpan = $dataContainer.find('span.data-cell');
        
        // current content
        var currentContent = {
            button: $this,
            cell: $dataSpan,
            row: row,
            col: col
        };
        
        var oldContent = contentEditable.pop();
        
        if (oldContent) {
            if (oldContent.row != row || oldContent.col != col){
                // save current content
                saveContent(currentContent);
            }
            // update old content
            updateContent(oldContent);
        }
        else {
            // save current content
            saveContent(currentContent);
        }
    });
}

function saveContent(content) {
    // store content
    contentEditable.push(content);
    
    // update cell and button
    content.button.text('\u2714');
    content.cell.attr('contenteditable', true);
    content.cell.addClass('lead');
    return false;
}

/**********************************
* Update a cell content in the data 
* table and pasedData varialble
* invoked from showData
***********************************/
function updateContent(content) {
    content.button.text('\u270D');
    var $cell = content.cell;
    var row = parseInt(content.row, 10);
    var col = parseInt(content.col, 10);
    var oldVal = jvData.jv[row][col];
    var newVal = $cell.text();
    var message;
    
    // update cell attributes 
    $cell.attr('contenteditable', false);
    $cell.removeClass('lead');
    
    // update cell content if the text is changed
    // and the text is a number
    if ( oldVal != newVal) {
        if (isNaN(newVal)) {
            content.cell.text(oldVal);
            message = 'Invalid data for "' + dataTableHeader[col] + 
                '" at row# '+ (row + 1) + '! Continuing with old data.';
            alertTable(message, 'fail');
        }
        else {
            jvData.jv[row][col] = newVal;
            message = '"' + dataTableHeader[col] + '" data at row# '+ (row + 1) + 
                ' has been updated. Previous value was ' + oldVal + '.'; 
            alertTable(message, 'success');
        }
    }
}

/**********************************
* Delete a cell in the data table
* invoked from showData
***********************************/
function deleteCell() {
    $('#table-container').on('click', '.cell-crossout', function() {
        var $cell = $(this).parent();
        var rowIndex = parseInt($cell.attr('row'), 10);
        var colIndex = parseInt($cell.attr('col'), 10);
        var message;
        
        // update parsed data 
        jvData.jv[rowIndex].splice(colIndex, 1);
        
        // remove the cell
        $cell.remove();
        
        // display message
        message = getDataInfo();
        message = 'Table cell at row# ' + (rowIndex + 1) + 
            ' and column# ' + (colIndex + 1) +
            ' has been deleted! ' + message;
        alertTable(message, 'warning');
    });
}

/**********************************
* Delete a row in the data table
* invoked from showData
***********************************/
function deleteRow() {
    var $tableContainer = $('#table-container');
    $tableContainer.on('click', '.row-crossout', function() {
        var message;
        var $row = $(this).parents(':eq(1)');
        var rowIndex = parseInt($row.attr('row'), 10);
        
        // update parsed data
        jvData.jv.splice(rowIndex, 1);
        
        // remove the row
        $row.remove();
        
        // show data in a table
        var alertType = jvData.jv.length ? 'success' : 'fail';
        
        if (alertType == 'success') {
            // show ajax loader
            $tableContainer.html(getAjaxLoader());
            showData(jvData.jv); 
            message = getDataInfo();
            message = 'Table row at ' + (rowIndex + 1) + 
                ' has been deleted! ' + message;
            alertType = 'warning';
        }
        else if (alertType == 'fail') {
            $('#table-container').html(null);
            message = 'There is no data in the table!';
        }
        
        alertTable(message, alertType);
        return false;
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
          if ($this.attr('name') != $(sl).attr('name') && 
            current == $(sl).val()) {
                $(sl).val(previous);
                previous = current;
            }
        });
        updateDataTableHeader();
    });
}

function updateDataTableHeader() {
    $('th select').each(function(i, sl) {
        dataTableHeader[i] = $(sl).val();
    });
}

/**********************************
* Show number of columns and rows in 
* the data table
* invoked from showData and deleteRow
***********************************/
function getDataInfo() {
    var jv = jvData.jv;
    var numRws = jv.length;
    var numCols = numRws ? jv[0].length : 0;
    
    var message = 'There are total ' + numRws + 
        ' row(s) and '+ numCols + 
        ' column(s) (based on first row) in the data.' +
        ' Please verify that the data has been parsed correctly.';
    return message;
}

/**********************************
* Show alert message for the data table
* invoked from showData
***********************************/
function alertTable(message, alertType, isTable=false) {
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
        if (isTable) {
            // create table show/hide button
            var $buttonShowHide = tableShowHide();
            $alertDivInfo.append($('<span/>', {
                text: '\xa0\xa0'
            })).append($buttonShowHide);
            // update visibility of close button
            if (!isTableVisible) {
                $buttonClose.hide();
            }
        }
        
        if (alertType == 'success') {
            // show alert type
            $alertType.text('Success:');
        
            // add appropriate class and add the show/hide button 
            $alertDiv.addClass('alert-info');
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
    return false;
}

/**********************************
* Create table show/hide button
* invoked from alertTable
***********************************/
function tableShowHide() {
    // create show/hide button
    var $buttonShowHide = $('<strong/>', {
        id: 'table-show-hide',
        class: 'cursor-pointer',
        text: isTableVisible ? 'Hide data table' : 'Show data table'
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
            $this.text('Show data table');
            $tableContainer.hide(500);
            $buttonClose.hide();
        }
        else {
            isTableVisible = true;
            $this.text('Hide data table');
            $buttonClose.show();
            $tableContainer.show();
            $('#analyze').show();
            if (!$('#raw-data').length) {
                // show ajax loader in the table container
                $tableContainer.html(getAjaxLoader());
                showData(jvData.jv);
            }
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

/**********************************
* Get JV data for analysis
* invoked from alertTable
***********************************/
function getJVData() {
    var voltage = [];
    var current = [];
    if ($('#table-container').find('#raw-data').length == 0) {
        dataTableHeader = ['voltage', 'current'];
    }
    var voltageIndex = dataTableHeader.indexOf('voltage');
    var currentIndex = dataTableHeader.indexOf('current');
    $(jvData.jv).each(function(i, row) {
        if (row.length >= 2) { 
        voltage.push(Number(row[voltageIndex]));    
        current.push(Number(row[currentIndex]));
        }
    });
    return [voltage, current];
}

/******************************************
* Upload JV data and show the results
* invoked by click event of upload button
******************************************/
function analyzeData() {
    $('#analyze').validator().on('submit', function(e){
        if (e.isDefaultPrevented()) {
            // form was not valid; show alert message
            alertTable("You are trying to submit an invalid form!", "fail");
        } 
        else {
            e.preventDefault();
            var data = $(this).serializeArray();
            var jv = getJVData();
            
            data.push({
                name: 'jv', 
                value: JSON.stringify(jv)
            });
            
            $.ajax({
                method: "POST",
                url: Flask.url_for("analyze"),
                data: data,
                dataType: "json"
            })
             .done(function(data) {
                var message = data.success || data.fail || data.warning;
                if (data.success || data.warning) {
                    // update jvData
                    jvData["data_id"] = data.data_id;
                    // show parameters in the tables
                    showPVParams(data);
                    showModelParams(data);
                    loadPlot();
                    // show results
                    $('#results').show();
                    // hide analyze form
                    $('#analyze').hide();
                    // hide data table
                    $('#table-container').hide();
                    isTableVisible = false;
                    var alertType;
                    if (data.success) {
                        alertType = "success";
                    }
                    else if (data.warning) {
                        alertType =  "warning";
                    }
                    // show alert message
                    alertTable(message, alertType);
                    // reset file object
                    $('#data-file').val('');
                    // update file control text area and alert box
                    $('.custom-file-control').text('Choose file ...');
                }
                else {
                    $('#results').hide();
                    // show alert message
                    alertTable(message, "fail");
                }
            })
             .fail(function (jqXHR, status) {
                $('#results').hide();
                // show alert message
                alertTable("There was something wrong receving the analyzed data!", "fail");
                console.log(jqXHR.statusText);
            });
        
        }
    });
}

/******************************************
* Upload JV data and show the results
* invoked by click event of upload button
******************************************/
function saveData() {
    $('#save').on('click', function(e){
        e.preventDefault();
        
        $.ajax({
            method: "POST",
            url: Flask.url_for("save"),
            data: {data_id: jvData.data_id},
            dataType: "json"
        })
         .done(function(data) {
            var message = data.success || data.fail;
            if (data.success) {
                // reset jvData
                jvData = {};
                // hide table show/hide button
                $('#table-container').html(null);
                // hide results
                $('#results').hide();
                // show alert message
                alertTable(message, "success");
            }
            else {
                $('#results').hide();
                // show alert message
                alertTable(message, "fail");
            }
        })
         .fail(function (jqXHR, status) {
            $('#results').hide();
            // show alert message
            alertTable("There was something wrong saving the analyzed data!", "fail");
            console.log(jqXHR.statusText);
        });
    });
}

/******************************************
* Show PV parameters in the table pv-params 
* invoked by uploadData
******************************************/
function showPVParams(paramsData) {
    var pvParams = ["voc", "jsc", "ff", "pec"];
    var $row = showParams(pvParams, paramsData);
    $('#pv-params').html($row);
}

/************************************************
* Show model parameters in the table model-params 
* invoked by uploadData
*************************************************/
function showModelParams(paramsData) {
    var modelParams = ["jnot", "ideality", "rseries", "rshunt"];
    var $row = showParams(modelParams, paramsData);
    $('#model-params').html($row);
}

/***********************************
* Show parameters in a row of table
* invoked by showPVParams/ModelParams
************************************/
function showParams(params, data) {
    var $row = $('<tr/>');
    $(params).each(function(i, param) {
        var parameter = data[param];
        $row.append($('<td/>', { 
            text: parameter >= 0.01 ? 
                numeral(parameter).format('0.00') : numeral(parameter).format('0.00e+0')
            })
        );
    });
    return $row;
}

function loadPlot() {
    // show ajax loader before loading the results
    $("#plot-container").html(getAjaxLoader());
    // load plot
    var url = Flask.url_for("plot", {data_type: 'temporary', data_id: jvData.data_id});
    $("#plot-container").load( url,
        function( response, status, xhr ) {
            if ( status == "error" ) {
                console.log( xhr.status + " " + xhr.statusText );
                alertTable("There was an error loading plot!", "fail");
            }
        }
    );
}

$(function(){
    $('body').on('click', '.close', function() {
        $('#lead-button').addClass('show');
    });
});