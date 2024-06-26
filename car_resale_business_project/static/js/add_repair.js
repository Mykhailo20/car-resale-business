// employee
var employeeSelect = document.getElementById('car-employee-mechanic-manager');
var noneOption = employeeSelect.querySelector('option[value="__None"]');
noneOption.disabled = true;
/*noneOption.removeAttribute('selected');*/
noneOption.setAttribute('hidden', 'hidden');

// repair-type
var transmissionSelect = document.getElementById('repair-type');
var newOption = '<option value="__None" hidden>Repair Type</option>';
transmissionSelect.insertAdjacentHTML('afterbegin', newOption);

function hideNoneOption(ids) {
    ids.forEach(id => {
      var select = document.getElementById(id);
      var noneOption = select.querySelector('option[value="__None"]');
      if(noneOption) {
        noneOption.setAttribute('hidden', 'hidden');
      }
    });
}

function addHideNoneOptions(idValuePairs) {
    idValuePairs.forEach(pair => {
      var select = document.getElementById(pair.id);
      var newOption = `<option value="__None" selected hidden>${pair.value}</option>`;
      select.insertAdjacentHTML('afterbegin', newOption);
      var noneOption = select.querySelector(`option[value="__None"]`);
      if(noneOption) {
        noneOption.disabled = true;
        noneOption.setAttribute('hidden', 'hidden');
      }
    });
}

var hideNonOptionIds = ['car-employee-mechanic-manager', 'repair-city'];
hideNoneOption(hideNonOptionIds);

var addHideNonOptionIds = [
    { id: 'repair-type', value: 'Repair Type' },
    { id: 'repair-car-condition', value: 'Condition' }
];

addHideNoneOptions(addHideNonOptionIds);