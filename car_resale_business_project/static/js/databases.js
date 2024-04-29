// Get the slider element
var slider = document.getElementById("records-no-slider");

// Get the span element to display the selected records
var selectedRecords = document.getElementById("selected-records");

// Update the span text when the slider value changes
slider.addEventListener("input", function() {
    selectedRecords.textContent = this.value;
});
