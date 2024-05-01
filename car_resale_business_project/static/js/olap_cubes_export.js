// Access properties of the olapMetadata object
console.log(olapMetadata);

// Function to create a new metrics container
function createNewMetricsContainer() {
    const newMetricsContainer = document.createElement("div");
    newMetricsContainer.classList.add("cubes-selection-container__logical-block-container__inputs");
    return newMetricsContainer;
}

document.addEventListener("DOMContentLoaded", function() {
    // Get references to the relevant elements
    const olapCubeSelect = document.getElementById("olap-cube-select");
    const metricsContainer = document.getElementById("cube-metrics-container");

    // To hide submit-tip
    const fileExtentionSelect = document.getElementById("file-extension-select");
    const fileNameInput = document.getElementById("file-name-input");
    const dateFromInput = document.getElementById("filter-date-from");
    const dateToInput = document.getElementById("filter-date-to");

    fileExtentionSelect.addEventListener("click", function(){
        messageContainer = document.getElementById('submit-tip')
        // Clear previous messages
        messageContainer.classList.add('hidden');
    })

    fileNameInput.addEventListener("click", function(){
        messageContainer = document.getElementById('submit-tip')
        // Clear previous messages
        messageContainer.classList.add('hidden');
    })

    dateFromInput.addEventListener("click", function(){
        messageContainer = document.getElementById('submit-tip')
        // Clear previous messages
        messageContainer.classList.add('hidden');
    })

    dateToInput.addEventListener("click", function(){
        messageContainer = document.getElementById('submit-tip')
        // Clear previous messages
        messageContainer.classList.add('hidden');
    })

    // Event listener for OLAP cube selection change
    olapCubeSelect.addEventListener("change", function() {

        // Remove all child elements with the specified class
        const inputsDivs = metricsContainer.querySelectorAll(".cubes-selection-container__logical-block-container__inputs");
        inputsDivs.forEach(div => {
            metricsContainer.removeChild(div);
        });

        messageContainer = document.getElementById('submit-tip')
        // Clear previous messages
        messageContainer.classList.add('hidden');

        const selectedCube = olapCubeSelect.value;
        const cubeMetadata = olapMetadata["facts"][selectedCube];
        console.log("selectedCube = ", selectedCube);
        console.log("cubeMetadata = ", cubeMetadata);
        
        // Populate Metrics container
        Object.keys(cubeMetadata.metrics).forEach((metricKey, index) => {
            const metric = cubeMetadata.metrics[metricKey];
            // Check if current container has reached 6 metrics
            if (index % metricsColsNo === 0) {
                // Create a new metrics container
                currentMetricsRowContainer = createNewMetricsContainer();
                metricsContainer.appendChild(currentMetricsRowContainer);
            }
            // Skip if the metric name contains an ID
            if (!metricKey.toLowerCase().includes("id")) {
                const metricCheckbox = document.createElement("div");
                metricCheckbox.classList.add(`col-md-${Math.floor(bootstrapColsNo / metricsColsNo)}`);
                metricCheckbox.innerHTML = `
                    <div class="form-check">
                        <input class="form-check-input export-cubes-check-input" type="checkbox" id="${metricKey}-checkbox">
                        <label class="form-check-label" for="${metricKey}-checkbox">
                            ${metric.name}
                        </label>
                    </div>
                `;
                currentMetricsRowContainer.appendChild(metricCheckbox);

                metricCheckbox.addEventListener('change', function() {
                    messageContainer = document.getElementById('submit-tip')
                    // Clear previous messages
                    messageContainer.classList.add('hidden');
                });
            }
        });
        

        /********************************* DIMENSIONS AND HIERARHIES ***************************************/
        // Populate Dimensions and Hierarchies container
        const dimsHiersContainer = document.querySelector('.cubes-selection-container__logical-block-container__inputs__dims-hiers');

        // Remove all child elements with the specified class
        const dimHierRowDivs = dimsHiersContainer.querySelectorAll(".cubes-selection-container__logical-block-container__inputs__dim-row");
        dimHierRowDivs.forEach(div => {
            dimsHiersContainer.removeChild(div);
        });

        // Iterate through each dimension
        cubeMetadata.dimensions.forEach((dimension, index) => {
            // Get the metadata for the current dimension
            const dimMetadata = olapMetadata.dimensions[dimension]; // Assuming olapMetadata is the metadata object

            // Create a new dimension row container
            const dimRowContainer = document.createElement('div');
            dimRowContainer.classList.add('cubes-selection-container__logical-block-container__inputs__dim-row');

            // Create the checkbox for the dimension
            const dimensionCheckbox = document.createElement('div');
            dimensionCheckbox.classList.add('form-check');
            dimensionCheckbox.classList.add('cubes-selection-container__logical-block-container__inputs__dim-row__dim-name');
            dimensionCheckbox.innerHTML = `
                <input class="form-check-input" type="checkbox" id="${dimension}-checkbox">
                <label class="form-check-label" for="${dimension}-checkbox">
                    ${dimMetadata.name}
                </label>
            `;
            dimRowContainer.appendChild(dimensionCheckbox);

            // Create the select for hierarchy level of the dimension
            const hierarchySelect = document.createElement('select');
            hierarchySelect.classList.add('export-cubes-hier-input');
            hierarchySelect.id = `${dimension}-levelSelect`;

            // Populate options for hierarchy levels
            dimMetadata.hierarchies.forEach((hierarchy, hierarchyIndex) => {
                const option = document.createElement('option');
                option.value = `${hierarchy}`; // maybe hierarchyIndex here
                option.text = `${hierarchy.join(' -> ')}`;
                hierarchySelect.appendChild(option);
            });
            hierarchySelect.disabled = true;

            // Append the select to the dimension row container
            dimRowContainer.appendChild(hierarchySelect);

            // Append the dimension row container to the parent container
            dimsHiersContainer.appendChild(dimRowContainer);

            // Add event listener to the checkbox to toggle the select
            const checkbox = document.getElementById(`${dimension}-checkbox`);
            checkbox.addEventListener('change', function() {
                messageContainer = document.getElementById('submit-tip')
                // Clear previous messages
                messageContainer.innerHTML = '';
                hierarchySelect.disabled = !this.checked;
            });
        });
    });

    // Simulate the selection of the "Purchase" cube
    olapCubeSelect.selectedCube = "Purchases";  // Set the value of the select element to "Purchases"
    olapCubeSelect.dispatchEvent(new Event('change'));  // Manually trigger the 'change' event
    console.log('imitate purchase cube selection')
});

// Get the form element
const form = document.getElementById('cubes-export-form');

// Add event listener for form submission
form.addEventListener('submit', function(event) {
   
    messageContainer = document.getElementById('submit-tip')
    // Clear previous messages
    messageContainer.innerHTML = '';
    
    // Get the metrics container
    const metricsContainer = document.querySelector('#cube-metrics-container');

    // Get the dimensions and hierarchies container
    const dimsHiersContainer = document.querySelector('.cubes-selection-container__logical-block-container-dims-hiers');

    // Check if at least one metric is selected
    const selectedMetrics = metricsContainer.querySelectorAll('input[type="checkbox"]:checked');
    if (selectedMetrics.length === 0) {
        event.preventDefault(); // Prevent form submission
        messageContainer.innerHTML = 'Please select at least one metric.'
        messageContainer.classList.remove('hidden'); // Show tip message
        return;
    }

    // Check if at least one dimension is selected
    const selectedDimsHiers = dimsHiersContainer.querySelectorAll('input[type="checkbox"]:checked');
    if (selectedDimsHiers.length === 0) {
        event.preventDefault(); // Prevent form submission 
        messageContainer.innerHTML = 'Please select at least one dimension.'
        messageContainer.classList.remove('hidden'); // Show tip message
        return;
    }

    // If both conditions are met, allow the form submission
    messageContainer.classList.add('hidden');
});