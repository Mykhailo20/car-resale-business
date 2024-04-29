// Get the button element
var fillOltpButton = document.getElementById("fill-oltp-btn");
var fillOlapButton = document.getElementById("fill-olap-btn");
var updateOlapButton = document.getElementById("update-olap-btn");

// Add event listener to the button
fillOltpButton.addEventListener("click", function() {
    fillOltpButton.disabled = true;
    // Get the value from the slider
    var selectedRecords = document.getElementById("selected-records").textContent;

    // Send a request to the 'fill_oltp' endpoint with the selected records number
    fetch(`/fill_oltp?records=${selectedRecords}`)
        .then(response => response.text())
        .then(data => {
            data = data.replace(/\n/g, '<br>');
            // Display the received message in the log text area
            var logText = document.getElementById("fill-oltp-log-text");
            logText.innerHTML += data; // Append a line break using HTML
            
            // Check if the error message is present
            if (data.includes("Error occurred during OLTP DB filling")) {
                // Enable the button
                fillOltpButton.disabled = false;
            } else {
                fillOlapButton.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error occurred during OLTP DB filling:', error);
            // Enable the button
            fillOltpButton.disabled = false;
        });
});

// Add event listener to the button
fillOlapButton.addEventListener("click", function() {
    fillOlapButton.disabled = true;

    // Send a request to the 'fill_oltp' endpoint with the selected records number
    fetch('/fill_olap')
        .then(response => response.text())
        .then(data => {
            data = data.replace(/\n/g, '<br>');
            // Display the received message in the log text area
            var logText = document.getElementById("etl-log-text");
            logText.innerHTML += data; // Append a line break using HTML
            
            // Check if the error message is present
            if (data.includes("Error occurred during OLAP DB filling")) {
                // Enable the button
                fillOlapButton.disabled = false;
            } else {
                updateOlapButton.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error occurred during OLAP DB filling:', error);
            // Enable the button
            fillOlapButton.disabled = false;
        });
});

// Add event listener to the button
updateOlapButton.addEventListener("click", function() {
    updateOlapButton.disabled = true;
    // Send a request to the 'fill_oltp' endpoint with the selected records number
    fetch('/update_olap')
        .then(response => response.text())
        .then(data => {
            data = data.replace(/\n/g, '<br>');
            // Display the received message in the log text area
            var logText = document.getElementById("etl-log-text");
            logText.innerHTML += data; // Append a line break using HTML
            updateOlapButton.disabled = false;
        })
        .catch(error => {
            console.error('Error occurred during OLTP DB updating:', error);
            updateOlapButton.disabled = false;
        });
});

// Get the slider element
var slider = document.getElementById("records-no-slider");

// Get the span element to display the selected records
var selectedRecordsNumber = document.getElementById("selected-records");

// Update the span text when the slider value changes
slider.addEventListener("input", function() {
    selectedRecordsNumber.textContent = this.value;
});
