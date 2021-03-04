$(document).ready(function(e) {   
    var workspace = document.getElementById("workspace").value;
    getModules(workspace);
 });


//Notification
(async () => {
    // create and show the notification
    const showNotification = () => {
        // create a new notification
        const notification = new Notification('Instruction', {
            body: 'To save outputs of modules use --output after command',
        });

        // close the notification after 5 seconds
        setTimeout(() => {
            notification.close();
        }, 5 * 1000);
    }
    let granted = false;

	if (Notification.permission === 'granted') {
	    granted = true;
	} else if (Notification.permission !== 'denied') {
	    let permission = await Notification.requestPermission();
	    granted = permission === 'granted' ? true : false;
	}

	// show notification or the error message 
	granted ? showNotification() : showError();

})();




//Summary
var summary; // saving data from workspace in summary globally

function showModules(){
	$('#module option:not(:first)').remove();
	var data = summary;
	var selected = document.getElementById('type').value;
	console.log(selected);
	for(module in data){
		if(data[module].split('/')[0] === selected){
			var opt = document.createElement('option');
			opt.innerText = data[module].split('/')[1];
			opt.value = data[module].split('/')[1];
			document.getElementById('module').appendChild(opt);
		}
	}
}

function runCommand(){
	var command =document.getElementById('module').value;
	command += " ";
	command+= document.getElementById('target').value;
	fetch('/api/run/',{
		method: 'POST',
		headers: {
			'Content-type': 'application/json'
		},
		body: JSON.stringify({
			'cmd': command
		})
	})
	.then(function (response) {
		if (response.ok) {
			return response.json();
		}
		return Promise.reject(response);
	}).then(function (data) {
		var outputs = data.output;
		document.getElementById('output').innerHTML = `<ul class="output" id = "outputs" onclick="this.style.height==='100%' ? this.style.height='40px' : this.style.height='100%'"><a data-toggle="tooltip" data-placement="bottom" title="Expand" onclick="this.innerText ==='▼' ? this.innerText='▲' : this.innerText='▼'">▼</a></ul>`;
		for(output in outputs){
			if(Array.isArray(outputs[output])){
				for(info in outputs[output]){
					var out = document.createElement('li');
					out.innerText = outputs[output][info];
					document.getElementById('outputs').appendChild(out);
				}
			}
			else{
				var out = document.createElement('li');
				out.innerText = outputs[output];
				document.getElementById('outputs').appendChild(out);
			}
		}

	}).catch(function (error) {
		console.warn('Something went wrong.', error);
	});
}


function displayData(data){
	var table = document.getElementById('dataTable');
	var row = table.insertRow(-1);
	row.className="table__row";
	var type = row.insertCell(-1);
	type.className = "table__data";
	type.innerHTML = `<select class="form-control" id = "type" onchange="showModules()"><option selected disabled>Select Target</option></select>`;
	var mod = row.insertCell(-1);
	mod.className = "table__data";
	mod.innerHTML = `<select class="form-control" id = "module" ><option selected disabled>Select Target</option></select>`;
	var target = row.insertCell(-1);
	target.className = "table__data";
	target.innerHTML = `<input class="form-control" id = "target"></input>`;
	var result = row.insertCell(-1);
	result.className = "table__data";
	result.id = "output";
	result.innerHTML = `<button type="button" class="btn btn-primary" id = "result" onclick = "runCommand()">Get Result</button>`;
	const types = new Set();
	for (module in data){
		if(!(types.has(data[module].split('/')[0]))){
			types.add(data[module].split('/')[0]);
			var opt = document.createElement('option');
			opt.innerText = data[module].split('/')[0];
			opt.value = data[module].split('/')[0];
			document.getElementById('type').appendChild(opt);
		}
	}
	console.log(data);
}

function getModules(workspace){
	$("#dataTable tr:not(:first)").remove();
	fetch('/api/run/',{
		method: 'GET',
		headers: {
			'Content-type': 'application/json'
		}
	})
	.then(function (response) {
		if (response.ok) {
			return response.json();
		}
		return Promise.reject(response);
	}).then(function (data) {
		displayData(data.modules);
		summary = data.modules;
	}).catch(function (error) {
		console.warn('Something went wrong.', error);
	});
}
