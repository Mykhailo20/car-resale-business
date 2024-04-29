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

        // Send AJAX request to fetch car trims for the selected brand and model
        console.log('send ajax request to get car trims for brand:', selectedBrand, 'and model:', selectedModel);
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/get_car_brand_model_trims/" + selectedBrand + "/" + selectedModel, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    // Parse the response JSON
                    var carTrims = JSON.parse(xhr.responseText);
                    console.log("carTrims = ", carTrims);

                    var trimSelect = document.getElementById('car-trim');
                    // Remove all options
                    trimSelect.innerHTML = `
                        <option value="" hidden>Trim</option>
                    `;
                    carTrims.forEach(function(trim) {
                        var option = document.createElement('option');
                        option.value = trim;
                        option.textContent = trim;
                        trimSelect.appendChild(option);
                    });
                    console.log('Trims for brand:', selectedBrand, 'and model:', selectedModel, 'are:', carTrims);
                    trimSelect.disabled = false;
                    trimSelect.title = '';
                } else {
                    console.error('Error fetching car trims for brand ', selectedBrand, 'and model ', selectedModel, ': ', xhr.statusText);
                }
            }
        };
        xhr.send();
    });
});