function addRowSendRequest(){
    
    var name = document.getElementById('id_column_name').value
    var type = document.getElementById("id_column_type").value
    
    var specific = NaN;

    if (type == "5"){
        specific = `Min: ${document.getElementById("id_min_range").value} Max: ${document.getElementById("id_max_range").value}`
    }else if (type == "4"){
        specific = document.getElementById("id_phone_numbers").value;
    }else{
        specific = NaN;
    }

    var order = document.getElementById("id_column_order").value
    
    data = {
    "name": name,
    "type": type,
    "specific": specific,
    "order":order
    }

    
    var xhr = new XMLHttpRequest();

    xhr.open('POST', '/add/');
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            location.reload();
        }
    };

    xhr.send(JSON.stringify(data));

}


document.addEventListener('DOMContentLoaded', function() {

    if (window.location.pathname.toString() == '/add/') {
        var select = document.getElementById("id_column_type")

        var urlDiv = document.getElementById('url');
        urlDiv.innerHTML = 'Текущий URL-адрес: ';

        select.addEventListener("change",function () {

        var range_block = document.getElementById("id_range_block")
        var phone_block = document.getElementById("id_phone_block") 

        console.log(select)

        if (select.value == "4"){
            phone_block.style.display = "block";
            range_block.style.display = "none";
        }
        else if (select.value == "5"){
            range_block.style.display = "flex";
            phone_block.style.display = "none";
        }else{
            range_block.style.display = "none";
            phone_block.style.display = "none";
        }
      })
    }
  });

function submitForm(id) {
    var form = document.getElementById(`id_delete_form_${id}`);
    form.submit();
}

function generateDataSet(dataset_id){
    
}


