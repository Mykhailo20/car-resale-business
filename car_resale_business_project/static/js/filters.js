// Function to handle filter change
function handleFilterChange() {
    // Get selected filter values
    var fromDate = document.getElementById("purchase-date-from").value;
    var toDate = document.getElementById("purchase-date-to").value;
    var seller = document.getElementById("seller-name").value;
    var location = document.getElementById("location-city").value;

    // Provide default values for null filters
    fromDate = fromDate || null; // Default to empty string if fromDate is null
    toDate = toDate || null; // Default to empty string if toDate is null
    seller = seller || "All"; // Default to "All" if seller is null
    location = location || "All"; // Default to "All" if location is null

    console.log("AJAX request will be made with the following filter values:");
    console.log("From Date:", fromDate);
    console.log("To Date:", toDate);
    console.log("Seller:", seller);
    console.log("Location:", location);
    
    // Prepare data to send in AJAX request
    var data = {
        fromDate: fromDate,
        toDate: toDate,
        seller: seller,
        location: location
    };

    // Make AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "last_purchased/filter", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Request successful, update car cards with fetched data
            var responseData = JSON.parse(xhr.responseText);
            console.log("responseData = ", responseData);
            // updateCarCards(responseData); // Function to update car cards
        }
    };
    xhr.send(JSON.stringify(data));
}

// Add event listeners to filters
var filters = document.querySelectorAll('.filter__filter-input');
filters.forEach(function(filter) {
    filter.addEventListener('change', handleFilterChange);
});