// Function to handle filter change
function handleFilterChange() {
    // Get selected filter values
    var fromDate = document.getElementById("purchase-date-from").value;
    var toDate = document.getElementById("purchase-date-to").value;
    var manufacture_year = document.getElementById("manufacture-year").value;
    var location = document.getElementById("location-city").value;

    // Provide default values for null filters
    fromDate = fromDate || null; // Default to empty string if fromDate is null
    toDate = toDate || null; // Default to empty string if toDate is null
    manufacture_year = manufacture_year || "All"; // Default to "All" if seller is null
    location = location || "All"; // Default to "All" if location is null
    
    // Prepare data to send in AJAX request
    var data = {
        from_date: fromDate,
        to_date: toDate,
        manufacture_year: manufacture_year,
        city: location
    };

    console.log('Send AJAX request to last_purchased/filter with filters ', data);

    // Make AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "last_purchased/filter", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Request successful, update car cards with fetched data
            var responseData = JSON.parse(xhr.responseText);
            console.log("responseData = ", responseData);
            updateCarCards(responseData);
        }
    };
    xhr.send(JSON.stringify(data));
}

// Add event listeners to filters
var filters = document.querySelectorAll('.filter__filter-input');
filters.forEach(function(filter) {
    filter.addEventListener('change', handleFilterChange);
});


function updateCarCards(purchasesData) {
    var carCardsContainer = document.querySelector('.car-cards');
    carCardsContainer.innerHTML = ''; // Clear the car cards container

    purchasesData.forEach(function(purchase) {
        var carCardHTML = `
            <div class="car-card">
                <div class="car-card__left-side">
                    <div class="car-card__left-side__car-image">
                        <img>
                    </div>
                    <button class="btn btn-outline-success details-btn">Details</button>
                </div>
                <div class="car-card__right-side">
                    <div class="car-card__right-side__car-details-header">
                        <h3 class="car-card__right-side__car-details-header__model-trim">${purchase.car.make.name} ${purchase.car.model} ${purchase.car.trim}</h3>
                        <p class="car-card__right-side__car-details-header__vin">vin: ${purchase.car.vin}</p>
                        <h3 class="car-card__right-side__car-details-header__price">${purchase.price} $</h3>
                    </div>
                    <hr class="car-card__hr">
                    <div class="car-card__right-side__car-details-body">
                        <div class="car-card__right-side__car-details-body__items">
                            <div class="car-card__right-side__car-details-body__items-col">
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/calendar-icon.png" alt="manufacture-year-icon" width="20px" title="Car Manufacture Year">
                                    <span>${purchase.car.manufacture_year}</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/car-mileage-icon.png" alt="mileage-icon" width="20px" title="Car Mileage">
                                    <span>${purchase.odometer} mi</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/transaction-date-icon.png" alt="date-icon" width="20px" title="Purchase Date">
                                    <span>${purchase.purchase_date}</span>
                                </div>
                            </div>
                            <div class="car-card__right-side__car-details-body__items-col">
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/transmission-icon.png" alt="transmission-icon" width="20px" title="Car Transmission">
                                    <span>${purchase.car.transmission}</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/color-icon.png" alt="color-icon" width="20px" title="Car Color">
                                    <span>${purchase.car.color.name}</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/location-icon.png" alt="location-icon" width="20px" title="Car Location">
                                    <span>${purchase.seller.address.city.name}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        
        carCardsContainer.innerHTML += carCardHTML;
    });
}