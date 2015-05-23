
/**** START CONSTANTS****/
//True or False
var DEBUG = true,
COLLECTIONJSON = "application/vnd.collection+json",
HAL = "application/hal+json",
INCOME_USER_PROFILE = "http://atlassian.virtues.fi:8090/display/PWP/Exercise+4#Exercise4-Forum_User",
EXPENSE_USER_PROFILE= "http://atlassian.virtues.fi:8090/display/PWP/Exercise+4#Exercise4-Forum_Message",
DEFAULT_DATATYPE = "json",
ENTRYPOINT = "/accounting/api/users/<nickname>" //Entry point is getUser()
/**** END CONSTANTS****/

/**** START RESTFUL CLIENT****/


/**** USER ****/
/*
getUser is the entrypoint of the application.
*/

function getUsers(){
    return $.ajax({
        url: "/accounting/api/users/",
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        $("#user_list").empty();
        //Extract the users
        var users = data.collection.items;
        for (var i=0; i < users.length; i++){
            var user = users[i].data[0].value;
            appendUserToList(user);
        }
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not get user's incomes");
    });
}

function getUser(URL) {
    var apiurl = URL;
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){
        //Remove old list of users, clear the form data hide the content information(no selected)
        $("#income_list").empty();
        $("#expense_list").hide();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }

        var name = data.firstname;
        /*if(name != "admin"){
            $("#add_user").hide();
            $("#delete_user").hide();
        }*/
        $("#name").text(name);
        $("#nickname").text(data.nickname);
        $("#birthday").text(data.birthday);
        $("#balance").text("Balance: " + data.balance);
        $("#email").text("email: " + data.email);
        $("#gender").text(data.gender);
        var id = data.id;


        //get the incomes and expenses
        //getIncomes(id);
        //getExpenses(id)
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        //Inform user about the error using an alert message.
        alert ("Could not fetch the list of users.  Please, try again");
    });
}

function addUser(apiurl, userData){
    userData = JSON.stringify(userData);
    return $.ajax({
        url: apiurl,
        type: "POST",
        //dataType:DEFAULT_DATATYPE,
        data:userData,
        processData:false,
        contentType: COLLECTIONJSON+";"+FORUM_USER_PROFILE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        alert ("User successfully added");
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("Could not create new user");
    });
}

function editUser(apiurl, template) {
    $.ajax({
        url: apiurl,
        type: "PUT",
        headers: {"Authorization":"admin"},
        contentType: COLLECTIONJSON+";"+FORUM_USER_PROFILE,
        processData:false,
        data:JSON.stringify(template)
        //TODO 4: Implement the handlers successful and failures responses accordding to the function documentation.
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        var url = apiurl.split("/");
        var userUrl = "/";
        for(var i = 1; i < url.length - 2; ++i){
            userUrl = userUrl.concat(url[i]);
            userUrl = userUrl.concat("/");
        }
        getUser(userUrl);
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not edit user's restricted profile");
    });
}

function deleteUser(apiurl) {
    $.ajax({
        url: apiurl,
        type: "DELETE",
        headers: {"authorization":"admin"},
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        alert ("The user has been deleted from the database");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("The user could not be deleted from the database");
    });
}

function appendUserToList(nickname){
    /* WE have to build the following HTML document
     <li>
     <div><p id="name">Nickname</p></div>
     </li>*/
    var $user = $("<li>").html(""+
        "<div class='name'><button class='btn btn-default deleteUser' type='button' id='delete_user'>"+nickname+"</button></div>"
    );
    //Append to list
    $("#user_list").append($user);
    // #deleteUser -> handleDeleteUser
    $("#delete_user").on("click", handleDeleteUser);

}

/**** INCOME ****/

function getIncomes(id){
    return $.ajax({
        url: "/accounting/api/user/" + id + "/incomes/",
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        //Extract the users
        var incomes = data.collection.items;
        for (var i=0; i < incomes.length; i++){
            var url = incomes[i].href;
            getIncome(url);
        }
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not get user's incomes");
    });
}

function getIncome(url){
    $.ajax({
        url: url,
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        var income_url = data._links.self.href;
        var source = data.source;
        var amount =  data.amount;
        var date= data.date;
        var description= data.description;
        appendIncomeToList(source, amount, date, description);

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert("Cannot get information from message: "+ apiurl);
    });

}

function addIncome(apiurl, userData){
    userData = JSON.stringify(userData);
    return $.ajax({
        url: apiurl,
        type: "POST",
        //dataType:DEFAULT_DATATYPE,
        data:userData,
        processData:false,
        contentType: COLLECTIONJSON+";"+FORUM_USER_PROFILE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        alert ("User successfully added");
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("Could not create new user");
    });
}

function editIncome(apiurl, template) {
    $.ajax({
        url: apiurl,
        type: "PUT",
        headers: {"Authorization":"admin"},
        contentType: COLLECTIONJSON+";"+FORUM_USER_PROFILE,
        processData:false,
        data:JSON.stringify(template)
        //TODO 4: Implement the handlers successful and failures responses accordding to the function documentation.
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        var url = apiurl.split("/");
        var userUrl = "/";
        for(var i = 1; i < url.length - 2; ++i){
            userUrl = userUrl.concat(url[i]);
            userUrl = userUrl.concat("/");
        }
        getUser(userUrl);
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not edit user's restricted profile");
    });
}

function deleteIncome(apiurl) {
    $.ajax({
        url: apiurl,
        type: "DELETE",
        headers: {"Authorization":"admin"},
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        alert ("The user has been deleted from the database");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("The user could not be deleted from the database");
    });
}

function appendIncomeToList(nickname){
    /* WE have to build the following HTML document
     <li>
     <p class="name">Source</p>
     <p class="name">Amount</p>
     <p class="date">date</p>
     <div class="message">description </div>
     </li>*/
    var $income = $("<li>").html(""+
        "<p class='name'>"+source+"</p>"+
        "<p class='name'>"+amount+"</p>"+
        "<p class='name'>"+date+"</p>"+
        "<div class='message'>"+description+"</div"
    );
    //Append to list
    $("#income_list").append($income);
}


/**** EXPENSE ****/

function getExpenses(id){
    return $.ajax({
        url: "/accounting/api/user/" + id + "/expenses/",
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        //Extract the users
        var expenses = data.collection.items;
        for (var i=0; i < expenses.length; i++){
            var url = expenses[i].href;
            getExpense(url);
        }
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not get user's expenses");
    });
}

function getExpense(url){
    $.ajax({
        url: url,
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        var expense_url = data._links.self.href;
        var source = data.source;
        var amount =  data.amount;
        var date= data.date;
        var description= data.description;
        appendExpenseToList(source, amount, date, description);

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert("Cannot get information from message: "+ apiurl);
    });

}

function addExpense(apiurl, expenseData){
    expenseData = JSON.stringify(expenseData);
    return $.ajax({
        url: apiurl,
        type: "POST",
        //dataType:DEFAULT_DATATYPE,
        data:expenseData,
        processData:false,
        contentType: COLLECTIONJSON+";"+FORUM_USER_PROFILE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        alert ("Expense successfully added");
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("Could not create new expense");
    });
}

function editExpense(apiurl, template) {
    $.ajax({
        url: apiurl,
        type: "PUT",
        headers: {"Authorization":"admin"},
        contentType: COLLECTIONJSON+";"+FORUM_USER_PROFILE,
        processData:false,
        data:JSON.stringify(template)
        //TODO 4: Implement the handlers successful and failures responses accordding to the function documentation.
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        var url = apiurl.split("/");
        var userUrl = "/";
        for(var i = 1; i < url.length - 2; ++i){
            userUrl = userUrl.concat(url[i]);
            userUrl = userUrl.concat("/");
        }
        getUser(userUrl);
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not edit user's restricted profile");
    });
}

function deleteExpense(apiurl) {
    $.ajax({
        url: apiurl,
        type: "DELETE",
        headers: {"Authorization":"admin"},
        dataType:DEFAULT_DATATYPE
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        alert ("The user has been deleted from the database");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("The user could not be deleted from the database");
    });
}

function appendExpenseToList(source, amount, date, description){
    /* WE have to build the following HTML document
     <li>
     <p class="name">Source</p>
     <p class="name">Amount</p>
     <p class="date">date</p>
     <div class="message">description </div>
     </li>*/
    var $expense = $("<li>").html(""+
        "<p class='name'>"+source+"</p>"+
        "<p class='name'>"+amount+"</p>"+
        "<p class='name'>"+date+"</p>"+
        "<div class='message'>"+description+"</div"
    );
    //Append to list
    $("#expense_list").append($expense);
}

/**** END RESTFUL CLIENT****/


/**** BUTTON HANDLERS ****/

/*
	Handler for the user_list li a.user_link element.
	This function modify the selected user in the user_list (using the .selected
	class) and call the getUser to retrieve user information.
	TRIGGER: Pressing the a.user_link  inside #user_list
*/
function handleGetUser(event) {
	if (DEBUG) {
		console.log ("Triggered handleGetUser")
	}
	//TODO 2
	// This event is triggered by the a.user_link element. Hence, $(this)
	// is the <a> that the user has pressed. $(this).parent() is the li element
	// containing such anchor.
	// Use the method event.preventDefault() in order to avoid default action
    // for anchor links.
	event.preventDefault();//Avoid default link behaviour
	// Remove the class "selected" from the previous #user_list li element and
	// add it to the current #user_list li element. Remember, the current 
	// #user_list li element is $(this).parent()

    // e.target is the clicked element!
    // If it was a list item
    $(this).parent().parent().children().each(function(){
        var user = $(this).children();
        if(user.hasClass("selected")){
            user.removeClass("selected");
        }
    });
    $(this).addClass("selected");
	// Finally extract the href attribute from the current anchor ($(this)
	// and call the  method getUser(url) to make the corresponding HTTP call 
	// to the RESTful API. You can extract an HTML attribute using the 
	// attr("attribute_name") method  from JQuery.
    var url = $(this).attr("href");
    getUser(url);

	return false; //IMPORTANT TO AVOID <A> DEFAULT ACTIONS
}


/**
 Creates User resource representation using the data from the form showed in the screen.
 Calls the method addUser to upload the new User resource to the Web service.
 TRIGGER: Submit button with value Create from form #create_user_form 
**/
function handleCreateUser(event){
	if (DEBUG) {
		console.log ("Triggered handleCreateUser")
	}
	event.preventDefault();
	var $form = $(this);
	$nickname = $form.children("input[name=nickname]");
	var nickname = $nickname.val();
	var template = serializeFormTemplate($form);
	var url = $form.attr("action");
	addUser(url, template, nickname);
	return false; //Avoid executing the default submit
}
/**
 Modifies current User_restricted resource representation using the data from the form showed in the screen.
 Calls the method editRestrictedUserProfile to upload the new user information to the Web service.
 TRIGGER: Submit button with Edit value from form #user_restricted_form
**/
function handleEditUser(event) {
	if (DEBUG) {
		console.log ("Triggered handleEdit")
	}
	event.preventDefault();
	var $form = $(this);
	var template = serializeFormTemplate($form);
	var url = $form.attr("action");
	editRestrictedUserProfile(url, template);
	return false; //Avoid executing the default submit
}


/**
Calls the function deleteUser to remove the current user from the Web service.
TRIGGER: Delete user button.
**/
function handleDeleteUser(event){
	//Extract the url of the resource from the form action attribute.
	if (DEBUG) {
		console.log ("Triggered handleDeleteUser")
	}

	var userurl = "/accounting/api/users/"+event.currentTarget.innerHTML+"/";
	deleteUser(userurl);
}

function handleDeleteUserList(event){
    //Extract the url of the resource from the form action attribute.
    if (DEBUG) {
        console.log ("Triggered handleDeleteUser")
    }
    var userurl = $(this).closest("form").attr("action");
    getUsers();
}

/**
Calls the function deleteMessage to remove the current message from the Web service.
TRIGGER: Delete message button.
**/
function handleDeleteMessage(event){
	if (DEBUG) {
		console.log ("Triggered handleDeleteMessage")
	}
	//TODO 2: 
	//	Extract the url of the resource to be deleted from the form action attribute.
    var messageurl = $(this).closest("form").attr("action");
	//  Call the method deleteMessage(messageurl).
    deleteMessage(messageurl);
}
/*
Calls to getUsersForm in order to extract the template and create the form. 
TRIGGER This method is called when #addUser is clicked
*/
function handleCreateUserForm(event){
	if (DEBUG) {
		console.log ("Triggered handleCreateUserForm")
	}
	//Call the API method to extract the template
	//$this is the href
	getUsersForm($(this).attr("href"))
	return false;
}
/**** END BUTTON HANDLERS ****/

/*** START ON LOAD ***/
//This method is executed when the webpage is loaded.
$(function(){

	//The handlers are:
    // #deleteUser -> handleDeleteUser
    $("#delete_user_list").on("click", handleDeleteUserList);
	// #addUser -> handleCreateUserForm
    $("#addUser").on("click", handleCreateUserForm);
	// #deleteMessage => handleDeleteMessage
    $("#messages").on("click", "div div form div span input", handleDeleteMessage);
	// li a.user_link => handleGetUser
    $("#user_list").on("click", "li a", handleGetUser);
	// Direct and delegated events from http://api.jquery.com/on/

	//Retrieve list of users from the server
    var entrypoint = "/accounting/api/users/"+getQueryVariable("nickname")+"/";
	getUser(entrypoint);
})

function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable){return pair[1];}
    }
    return(false);
}
/*** END ON LOAD**/