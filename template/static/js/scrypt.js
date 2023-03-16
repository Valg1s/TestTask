
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
            const response = JSON.parse(xhr.responseText);
            const table = document.getElementById("id_columns_table");

            table.innerHTML += response.html;
            
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
    var rows = document.getElementById("rows").value

    if (rows){
        var data = {
            "rows": rows,
        }
        
        var table = document.getElementById("id_csv_sets_table")
        var row = document.createElement("tr");

        var counter = 1;
        var last_counter = document.querySelectorAll("#id_counter")

        if (last_counter.length > 0){
            counter = parseInt(last_counter[last_counter.length - 1].textContent) + 1
        }
        
        var dt = new Date();
        
        var html = `<td class="content__td-number" id="id_counter"> ${counter} </td>
        <td class="content__td-title"> ${dt.getFullYear() + "-" + (dt.getUTCMonth() + 1) + "-" + dt.getDate()} </td>
        <td> <p id="id_status_${counter}" class="content__dataset-proccesing" >Proccesing</p>  </td>
        <td id="id_link_block_${counter}" class="content__td-action"> </td>
        `;
        
        row.innerHTML = html;
        table.appendChild(row)

        axios.post(`/${dataset_id}/dataset/`,data,
            { headers: {
                'Content-Type': 'application/json'
                }
            }
            ).then(
                function (response){
                    var status = document.getElementById(`id_status_${counter}`);
                    status.className = "content__dataset-ready";
                    status.textContent = "Ready";
    
                    var link_block = document.getElementById(`id_link_block_${counter}`);
                    var link = document.createElement("a");
                    link.href = response.data['download_link'];
                    link.textContent = "Download";
                    link.className = "content__dataset-link-download";
                    link_block.appendChild(link);    
                }
            )
    }
}


