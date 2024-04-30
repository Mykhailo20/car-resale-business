function expandData(index) {
    const block = document.getElementById(`item_${index}`)
    const blockData = block.querySelector('.car-history__item__data')
    if(blockData.style.display === 'block') {
        blockData.style.display = 'none'
    } else {
        blockData.style.display = 'block'
    }
}

function expandRepairData(index) {
    const block = document.getElementById(`item_${index}`)
    const repairBlockData = block.querySelector('.car-history__repairs')
    if(repairBlockData.style.display === 'block') {
        repairBlockData.style.display = 'none'
    } else {
        repairBlockData.style.display = 'block'
    }
}

function expandChild(index) {
    const block = document.getElementById(`repair_${index}`)
    // const blockData = block.querySelector('.repair-content')
    const blockData = block.querySelector('.car-history__item__data')
    if(blockData.style.display === 'block') {
        blockData.style.display = 'none'
    } else {
        blockData.style.display = 'block'
    }
}
document.getElementById("go-back-btn").addEventListener("click", () => {
  history.back();
});

var closeButtons = document.querySelectorAll('.flash-close-btn');
closeButtons.forEach(function(button) {
    button.addEventListener('click', function() {
        var alertDiv = button.closest('.alert');
        if (alertDiv) {
            alertDiv.remove();
        }
    });
});