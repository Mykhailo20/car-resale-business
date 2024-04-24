window.addEventListener('DOMContentLoaded', function() {
    var brandSelect = document.getElementById('car-filter-brand');
    var noneOption = brandSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    var modelSelect = document.getElementById('car-filter-model');
    var noneOption = modelSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    var bodyTypeSelect = document.getElementById('car-filter-body_type');
    var noneOption = bodyTypeSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    var transmissionSelect = document.getElementById('car-filter-transmission');
    var noneOption = transmissionSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    // car-filter-seller-name
    var sellerSelect = document.getElementById('car-filter-seller-name');
    var noneOption = sellerSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    // car-filter-city
    var citySelect = document.getElementById('car-filter-city');
    var noneOption = citySelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    // car-filter-manufacture-year
    var manufactureYearSelect = document.getElementById('car-filter-manufacture-year');
    var noneOption = manufactureYearSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    // car-filter-condition
    var conditionSelect = document.getElementById('car-filter-condition');
    var noneOption = conditionSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    // car-filter-odometer
    var odometerSelect = document.getElementById('car-filter-odometer');
    var noneOption = odometerSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');

    // car-filter-choice
    var filterChoiceSelect = document.getElementById('car-filter-choice');
    var noneOption = filterChoiceSelect.querySelector('option[value="__None"]');
    noneOption.setAttribute('hidden', 'hidden');
});

document.addEventListener("DOMContentLoaded", function() {
    // Find the brand select element
    var brandSelect = document.getElementById('car-filter-brand');
    
    // Add event listener for change event
    brandSelect.addEventListener('change', function() {
        var selectedBrand = this.value;
        
        // Send AJAX request to fetch models for the selected brand
        console.log('send ajax request to get car models for ', selectedBrand);
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/get_car_brand_models/" + selectedBrand, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    // Clear existing options
                    var modelSelect = document.getElementById('car-filter-model');
                    
                    // Remove all options
                    /*
                    while (modelSelect.firstChild) {
                        modelSelect.removeChild(modelSelect.firstChild);
                    }
                    */
                    modelSelect.innerHTML = '';
                    
                    // Parse the response JSON
                    var response = JSON.parse(xhr.responseText);

                    console.log('response for the ajax = ', response);
                    console.log('response.car_models for the ajax = ', response.car_models);
                    response_car_models = response.car_models
                    // Add new options based on the response
                    response_car_models.forEach(function(car) {
                        var option = document.createElement('option');
                        option.value = car.model;
                        option.textContent = car.model; // Access the model property of each object
                        modelSelect.appendChild(option);
                    });
                    
                    // Enable the model select field
                    modelSelect.disabled = false;
                } else {
                    console.error('Error fetching models:', xhr.statusText);
                }
            }
        };
        xhr.send();
    });
});

