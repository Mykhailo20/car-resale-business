// Function to handle filter change
function handleFilterChange(event) {
    var element = event?.target;
    if (element && (element.id === 'car-brand')) {
        // Reset the model select element
        document.getElementById('car-model').value = '';
    }
    
    // Get selected filter values
    var fromDate = document.getElementById("date-from").value;
    var toDate = document.getElementById("date-to").value;
    var brand = document.getElementById("car-brand").value;
    var model = document.getElementById("car-model").value;
    var bodyType = document.getElementById("car-body-type").value;
    var manufactureYear = document.getElementById("manufacture-year").value;
    var transmission = document.getElementById("car-transmission").value;
    var location = document.getElementById("location-city").value;

    // Provide default values for null filters
    fromDate = fromDate || null;
    toDate = toDate || null;
    brand = brand || null;
    bodyType = bodyType || null;
    manufactureYear = manufactureYear || "All";
    transmission = transmission || "All";
    location = location || "All"; 
    
    // Prepare data to send in AJAX request
    var data = {
        sale_car_vin: '',
        sale_date_from: fromDate,
        sale_date_to: toDate,
        sale_brand: brand,
        sale_model: model,
        sale_body_type: bodyType,
        sale_manufacture_year: manufactureYear,
        sale_transmission: transmission,
        sale_city: location
    };

    console.log('Send AJAX request to last_sold/filter with filters ', data);

    // Make AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "last_sold/filter", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Request successful, update car cards with fetched data
            var responseData = JSON.parse(xhr.responseText);
            console.log("responseData = ", responseData);
            updateCarCards(responseData['transactionName'], responseData['transactionData'], responseData['mainPage'], responseData['pages'], responseData['urls'], responseData['purchases']);
        }
    };
    xhr.send(JSON.stringify(data));
}

var filters = document.querySelectorAll('.filter__filter-input');
filters.forEach(function(filter) {
    filter.addEventListener('change', function(event) {
        handleFilterChange(event); // Pass the event to handleFilterChange function
    });
});


function updateCarCards(transactionName, transactionData, mainPage, pages, urls, purchases) {
    var carCardsContainer = document.querySelector('.car-cards');
    var carCards = document.querySelectorAll('.car-card');
    carCards.forEach(function(card) {
        card.remove();
    });

    var noCarsMsg = document.querySelectorAll('.no-cars-found-message');
    noCarsMsg.forEach(function(msg) {
        msg.remove();
    });

    // Generate pagination buttons
    var paginationContainer = document.querySelector('.car-cards-pagination');
    paginationContainer.innerHTML = ''; // Clear the pagination container

    if (transactionData.length === 0) {
        carCardsContainer.innerHTML = `
        <div class="no-cars-found-message">
            <p>No cars were found for the specified parameters</p>
        </div>`;
        return; // Exit the function early
    }
    var transaction_index = 0;
    transactionData.forEach(function(transaction) {
        var transaction_date = '';
        var transaction_city = '';
        if(transactionName === 'Purchase') {
            transaction_date = transaction.purchase_date;
            transaction_city = transaction.seller.address.city.name;
        } else if(transactionName === 'Sale') {
            transaction_date = transaction.sale_date;
            transaction_city = transaction.buyer.address.city.name;
        }
        
        var carCardHTML = `
            <div class="car-card">
                <div class="car-card__left-side">
                    <div class="car-card__left-side__car-image">
                        ${transaction.car_image_content_type ? `<img src="data:${transaction.car_image_content_type};base64,${transaction.car_image}" alt="Car Image" class="car-img">` : ''}
                        ${!transaction.car_image_content_type && purchases.length > 0 && purchases[transaction_index].car_image_content_type ? `<img src="data:${purchases[transaction_index].car_image_content_type};base64,${purchases[transaction_index].car_image}" alt="Car Image" class="car-img">` : ''}
                    </div>
                    <a href="/car/${transaction.car.vin}" class="btn btn-outline-success details-btn">Details</a>
                </div>
                <div class="car-card__right-side">
                    <div class="car-card__right-side__car-details-header">
                        <h3 class="car-card__right-side__car-details-header__model-trim">${transaction.car.make.name} ${transaction.car.model} ${transaction.car.trim}</h3>
                        <p class="car-card__right-side__car-details-header__vin">vin: ${transaction.car.vin}</p>
                        <h3 class="car-card__right-side__car-details-header__price">${transaction.price} $</h3>
                    </div>
                    <hr class="car-card__hr">
                    <div class="car-card__right-side__car-details-body">
                        <div class="car-card__right-side__car-details-body__items">
                            <div class="car-card__right-side__car-details-body__items-col">
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/calendar-icon.png" alt="manufacture-year-icon" width="20px" title="Car Manufacture Year">
                                    <span>${transaction.car.manufacture_year}</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/car-mileage-icon.png" alt="mileage-icon" width="20px" title="Car Mileage">
                                    <span>${transaction.odometer} mi</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/transaction-date-icon.png" alt="date-icon" width="20px" title="${transactionName} Date">
                                    <span>${transaction_date}</span>
                                </div>
                            </div>
                            <div class="car-card__right-side__car-details-body__items-col">
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/transmission-icon.png" alt="transmission-icon" width="20px" title="Car Transmission">
                                    <span>${transaction.car.transmission}</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/color-icon.png" alt="color-icon" width="20px" title="Car Color">
                                    <span>${transaction.car.color.name}</span>
                                </div>
                                <div class="car-card__right-side__car-details-body__item">
                                    <img src="../static/images/icons/location-icon.png" alt="location-icon" width="20px" title="Car Location">
                                    <span>${transaction_city}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        carCardsContainer.innerHTML += carCardHTML;
        transaction_index += 1;
    });

    if (pages.length > 1) {
        if (pages.has_prev) {
            paginationContainer.innerHTML += `
            <div class="car-cards-pagination__item">
                <a href="${mainPage ? urls['last_transaction'] : urls['search_results']}" class="btn btn-outline-success btn-sm">Next</a>
            </div>`;
        }

        pages.forEach(function(page_num) {
            if (page_num) {
                if (page_num === 1) {
                    paginationContainer.innerHTML += `
                    <div class="car-cards-pagination__item">
                        <a href="${mainPage ? urls['last_transaction'][page_num] : urls['search_results'][page_num]}" class="btn btn-success btn-sm">${page_num}</a>
                    </div>`;
                } else {
                    paginationContainer.innerHTML += `
                    <div class="car-cards-pagination__item">
                        <a href="${mainPage ? urls['last_transaction'][page_num] : urls['search_results'][page_num]}" class="btn btn-outline-success btn-sm">${page_num}</a>
                    </div>`;
                }
            } else {
                paginationContainer.innerHTML += `
                <div class="car-cards-pagination__item">...</div>`;
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Find the brand select element
    var brandSelect = document.getElementById('car-brand');
    
    // Add event listener for change event
    brandSelect.addEventListener('change', function() {
        //handleFilterChange('car-brand');

        var selectedBrand = this.value;
        // Send AJAX request to fetch models for the selected brand
        console.log('send ajax request to get car models for ', selectedBrand);
        var xhrModels = new XMLHttpRequest();
        xhrModels.open("GET", "/get_car_brand_models/" + selectedBrand, true);
        xhrModels.onreadystatechange = function() {
            if (xhrModels.readyState === 4) {
                if (xhrModels.status === 200) {
                    // Clear existing options
                    var modelSelect = document.getElementById('car-model');
                    
                    // Remove all options
                    modelSelect.innerHTML = `
                        <option value="" hidden>Model</option>
                        <option value="All">All</option>
                    `;
                    
                    // Parse the response JSON
                    var responseModels = JSON.parse(xhrModels.responseText);
                    var carModels = responseModels.car_models;

                    // Add new options based on the response
                    carModels.forEach(function(model) {
                        var option = document.createElement('option');
                        option.value = model.model;
                        option.textContent = model.model;
                        modelSelect.appendChild(option);
                    });
                    
                    // Enable the model select field
                    modelSelect.disabled = false;
                    modelSelect.title = '';
                } else {
                    console.error('Error fetching models:', xhrModels.statusText);
                }
            }
        };
        xhrModels.send();

        // After fetching models, also fetch body types
        console.log('send ajax request to get car body types for ', selectedBrand);
        var xhrBodyTypes = new XMLHttpRequest();
        xhrBodyTypes.open("GET", "/get_car_brand_body_types/" + selectedBrand, true);
        xhrBodyTypes.onreadystatechange = function() {
            if (xhrBodyTypes.readyState === 4) {
                if (xhrBodyTypes.status === 200) {
                    // Parse the response JSON
                    var responseBodyTypes = JSON.parse(xhrBodyTypes.responseText);
                    var carBodyTypes = responseBodyTypes.car_body_types;
                    console.log("responseBodyTypes = ", carBodyTypes);

                    var bodyTypeSelect = document.getElementById('car-body-type');
                    // Remove all options
                    bodyTypeSelect.innerHTML = `
                        <option value="" hidden>Body</option>
                        <option value="All">All</option>
                    `;
                    carBodyTypes.forEach(function(body_type) {
                        var option = document.createElement('option');
                        option.value = body_type.body_type_id;
                        option.textContent = body_type.body_type_name;
                        bodyTypeSelect.appendChild(option);
                    });
                } else {
                    console.error('Error fetching body types:', xhrBodyTypes.statusText);
                }
            }
        };
        xhrBodyTypes.send();
    });

    // Find the model select element
    var modelSelect = document.getElementById('car-model');

    // Add event listener for change event
    modelSelect.addEventListener('change', function() {
        var selectedBrand = document.getElementById('car-brand').value;
        var selectedModel = this.value;

        // Send AJAX request to fetch body types for the selected brand and model
        console.log('send ajax request to get body types for brand:', selectedBrand, 'and model:', selectedModel);
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/get_car_brand_model_body_types/" + selectedBrand + "/" + selectedModel, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    // Parse the response JSON
                    var responseBodyTypes = JSON.parse(xhr.responseText);
                    var carBodyTypes = responseBodyTypes.car_body_types;
                    console.log("responseBodyTypes = ", carBodyTypes);

                    var bodyTypeSelect = document.getElementById('car-body-type');
                    // Remove all options
                    bodyTypeSelect.innerHTML = `
                        <option value="" hidden>Body</option>
                        <option value="All">All</option>
                    `;
                    carBodyTypes.forEach(function(body_type) {
                        var option = document.createElement('option');
                        option.value = body_type.body_type_id;
                        option.textContent = body_type.body_type_name;
                        bodyTypeSelect.appendChild(option);
                    });
                    console.log('Body types for brand:', selectedBrand, 'and model:', selectedModel, 'are:', carBodyTypes);
                } else {
                    console.error('Error fetching body types:', xhr.statusText);
                }
            }
        };
        xhr.send();
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Find the reset filters button
    var resetFiltersBtn = document.getElementById('reset-filters-btn');
    
    // Add event listener for click event
    resetFiltersBtn.addEventListener('click', function() {
        // Reset all filter values
        document.getElementById('date-from').value = '';
        document.getElementById('date-to').value = '';
        document.getElementById('car-brand').value = '';
        document.getElementById('car-model').value = '';
        document.getElementById('car-body-type').value = '';
        document.getElementById('manufacture-year').value = '';
        document.getElementById('car-transmission').value = '';
        document.getElementById('location-city').value = ''; 

        handleFilterChange();
    });
});
