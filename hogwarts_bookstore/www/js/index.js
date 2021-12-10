/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

// Wait for the deviceready event before using any of Cordova's device APIs.
// See https://cordova.apache.org/docs/en/latest/cordova/events/events.html#deviceready
document.addEventListener('deviceready', onDeviceReady, false);

function onDeviceReady() {
    // Cordova is now initialized. Have fun!

    console.log('Running cordova-' + cordova.platformId + '@' + cordova.version);
    document.getElementById('deviceready').classList.add('ready');
}

/* ===============================================*/
/*    VARIABLES */
/* ===============================================*/
let token = undefined;  // web token to authenticate the user
let map_of_books;       // map storing the title and price of books

/* ===============================================*/
/*    LOGIN */
/* ===============================================*/
function login() {
    if ($("#login-username").val().length === 0 || $("#login-password").val().length === 0) {
        alert("Username and password cannot be empty.");
        return;
    }

    // POST the entered credentials and determine how to proceed
    $.post("/open_api/login", {username: $("#login-username").val(), password: $("#login-password").val()})
        .done(function(data, status) {
            if (data.authenticated) {
                token = data.token;
                $("#main").hide();
                $("#app").show();
                loadBookStore();
            }
        })
        .fail(function(response) {
            alert("Incorrect username or password.");
        });
}

/* ===============================================*/
/*    SIGNUP */
/* ===============================================*/
function signup() {
    if ($("#signup-username").val().length === 0 || $("#signup-password").val().length === 0) {
        alert("Username and password cannot be empty.");
        return;
    }

    // POST the entered credentials and determine how to proceed
    $.post("/open_api/signup", {username: $("#signup-username").val(), password: $("#signup-password").val()})
        .done(function(data, status) {
            if (data.authenticated) {
                token = data.token;
                $("#main").hide();
                $("#app").show();
                loadBookStore();
            }
        })
        .fail(function(response) {
            alert("Username is already in use.");
        });
}

/* ===============================================*/
/*    BOOKSTORE */
/* ===============================================*/
function loadBookStore() {
    map_of_books = new Map();

    secure_get_with_token("/secure_api/get_books", {},
    function(data) {
        // display the username
        $("#greeting").html(`Hello, ${data.username}!`);

        // populate the drop down with books available to purchase
        $.each(data.books, function(index, book) {
            $('<option>').val(book.title).text(book.title).appendTo('#book-selection');
            map_of_books.set(book.title, book.price);
        });
        
        updatePrice();
    }, function(err) { 
        console.log(err) 
    });
}

function logout() {
    // reset variables and html elements
    token = undefined;
    map_of_books = undefined;

    $('#book-selection').empty();
    $('#price').text("");

    $("#app").hide();
    $("#main").show();
    $("#main").load(location.href + " #main");
}

function purchase_book() {
    let selected_book = $("#book-selection").val();

    secure_get_with_token("/secure_api/purchase_book", {"selected_book": selected_book}, 
    function(data) {
        if (!data.purchase_success) {
            alert(`Oops, looks like you already purchased ${selected_book}!`);
        } else {
            alert(`Successfully purchased ${selected_book}!`);
            token = data.token;
        }
    }, function(err) {
        console.log(err);
    });
}

function updatePrice() {
    // get the selected book's title
    let selected_book = $("#book-selection").val();

    // used for animation starting price
    let start_price = ($("#price").text().length > 0) ? parseFloat($("#price").text()) : 99.99;
    
    // populate the price element with the selected book's price
    $("#price").html(map_of_books.get(selected_book));

    // disable the buy button until the animation is finished
    $("#buy-book").prop("disabled", true);

    // fancy price animation
    $('.count').each(function () {
        var $this = $(this);
        jQuery({ Counter: start_price }).animate({ Counter: $this.text() }, {
            duration: 4000,
            easing: 'swing',
            step: function () {
                $this.text(this.Counter.toFixed(2));
            },
            done: function() {
                $("#buy-book").prop("disabled", false);
            }
        });
    });
}

/* ===============================================*/
/*    UTILITY */
/* ===============================================*/
function secure_get_with_token(endpoint, data_to_send, on_success_callback, on_fail_callback) {
	xhr = new XMLHttpRequest();
	function setHeader(xhr) {
		xhr.setRequestHeader('Authorization', 'Bearer:'+token);
	}

	$.ajax({
		url: endpoint,
		data : data_to_send,
		type: 'GET',
		datatype: 'json',
		success: on_success_callback,
		error: on_fail_callback,
		beforeSend: setHeader
	});
}