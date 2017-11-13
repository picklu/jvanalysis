var parsedData;

function readTextFile(event) 
{
    document.getElementById('raw-data').innerHTML = null;
    var file = event.target.files[0];
    if (!file) { return;}
    var reader = new FileReader();
    reader.onload = (e) => {
        var text = e.target.result;
        parsedData = Papa.parse(text).data;
        localStorage.setItem('file', JSON.stringify({
            fname: file.name,
            content: text,
            jsonFile:  parsedData
        }));
        var table = document.getElementById('raw-data');
        parsedData.forEach((row, i) => {
            if (i == 0) {
                var rowTable = document.createElement("tr");
                rowTable.innerHTML = `<th>#</th>`;
                row.forEach((col, j) => {
                rowTable.innerHTML += `<th>Col#${j+1}</th>`;
                });
                table.append(rowTable);
            }
            var rowTable = document.createElement("tr");
            rowTable.innerHTML = `<th>${i+1}</th>`;
            row.forEach((col, j) => {
                rowTable.innerHTML += `<td>${col}</td>`;
            });
            table.append(rowTable);
        });
    };
    reader.readAsText(file);
}