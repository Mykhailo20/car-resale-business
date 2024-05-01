// employee
var employeeSelect = document.getElementById('car-employee-mechanic-manager');
var noneOption = employeeSelect.querySelector('option[value="__None"]');
noneOption.disabled = true;
/*noneOption.removeAttribute('selected');*/
noneOption.setAttribute('hidden', 'hidden');

// repair-type
var repairTypeSelect = document.getElementById('repair-type');
var newOption = '<option value="__None" hidden>Repair Type</option>';
repairTypeSelect.insertAdjacentHTML('afterbegin', newOption);