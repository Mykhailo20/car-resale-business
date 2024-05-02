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

var hideNonOptionIds = ['car-employee-seller', 'buyer-city'];
hideNoneOption(hideNonOptionIds);

var addHideNonOptionIds = [
    { id: 'buyer-sex', value: 'Sex' },
    { id: 'sale-car-condition', value: 'Condition' }
];

addHideNoneOptions(addHideNonOptionIds);