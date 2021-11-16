var jwt = Cookies.get("token");

function secure_get_with_token(endpoint, on_success_callback, on_fail_callback){
	xhr = new XMLHttpRequest();
	function setHeader(xhr) {
		xhr.setRequestHeader('Authorization', 'Bearer:'+jwt);
	}
	function get_and_set_new_jwt(data){
		console.log(data);
		jwt = data.token
		on_success_callback(data)
	}
	$.ajax({
		url: endpoint,
		type: 'GET',
		datatype: 'json',
		success: on_success_callback,
		error: on_fail_callback,
		beforeSend: setHeader
	});
}

function secure_get_with_data_and_token(endpoint, data, on_success_callback, on_fail_callback){
	xhr = new XMLHttpRequest();
	function setHeader(xhr) {
		xhr.setRequestHeader('Authorization', 'Bearer:'+jwt);
	}
	function get_and_set_new_jwt(data){
		console.log(data);
		jwt = data.token
		on_success_callback(data)
	}
	$.ajax({
		url: endpoint,
		type: 'GET',
		datatype: 'json',
		data: data,
		success: on_success_callback,
		error: on_fail_callback,
		beforeSend: setHeader
	});
}
