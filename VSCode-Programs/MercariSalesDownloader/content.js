function downloadCSV(data) {
    var blob = new Blob([data], {type: 'text/csv'});
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'sales_data.csv';

    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
}

function scrapeSalesData() {
    // You'll need to implement the actual data scraping logic here.
    var salesData = "Date,Item,Price\n2023-09-29,Item A,1000\n2023-09-30,Item B,1500";
    downloadCSV(salesData);
}

var downloadButton = document.createElement('button');
downloadButton.textContent = 'Download Sales Data';
downloadButton.onclick = scrapeSalesData;
document.body.appendChild(downloadButton);