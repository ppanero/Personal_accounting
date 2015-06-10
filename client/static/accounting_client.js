
/**** START CONSTANTS****/
//True or False
var DEBUG = true,
COLLECTIONJSON = "application/vnd.collection+json",
HAL = "application/hal+json",
INCOME_USER_PROFILE = "http://atlassian.virtues.fi:8090/display/PWP/Exercise+4#Exercise4-Forum_User",
EXPENSE_USER_PROFILE= "http://atlassian.virtues.fi:8090/display/PWP/Exercise+4#Exercise4-Forum_Message",
DEFAULT_DATATYPE = "json",
ENTRYPOINT = "/accounting/api/users/<nickname>" //Entry point is getUser()
var currentUserId = 0;
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
        $("#expense_list").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }

        var name = data.nickname;
        if(name != "admin"){
            $("#add_user_list").hide();
            $("#delete_user_list").hide();
        }
        $("#name").text(name);
        $("#nickname").text(data.nickname);
        $("#birthday").text(data.birthday);
        $("#balance").text("Balance: " + data.balance);
        $("#email").text("email: " + data.email);
        $("#gender").text(data.gender);
        var id = data.id;
        currentUserId = id;


        //get the incomes and expenses
        getIncomes("/accounting/api/user/" + id + "/incomes/");
        getExpenses("/accounting/api/user/" + id + "/expenses/");
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
        contentType: COLLECTIONJSON
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
        contentType: COLLECTIONJSON,
        processData:false,
        data:JSON.stringify(template)
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        getUser(ENTRYPOINT);
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

function getIncomes(apiurl){
    return $.ajax({
        url: apiurl,
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
        var id = data._id;
        appendIncomeToList(source, amount, date, description, id);

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
        contentType: COLLECTIONJSON
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
        }
        alert ("Income successfully added");
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("Could not create new income");
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
        alert ("The income has been deleted from the database");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
        }
        alert ("The income could not be deleted from the database");
    });
}

function appendIncomeToList(source, amount, date, description, id){
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
        "<button class='deleteItem' type='button' id='delete_income"+id+"'>Delete </button>"+
        "<div class='message'>"+description+"</div>"

    );
    //Append to list
    $("#income_list").append($income);
    $("#delete_income"+id).on("click", handleDeleteIncome);
}


/**** EXPENSE ****/

function getExpenses(apiurl){
    return $.ajax({
        url: apiurl,
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
        var id = data._id;
        appendExpenseToList(source, amount, date, description, id);

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

function appendExpenseToList(source, amount, date, description, id){
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
        "<button class='deleteItem' type='button' id='delete_expense"+id+"'>Delete </button>"+
        "<div class='message'>"+description+"</div>"
    );
    //Append to list
    $("#expense_list").append($expense);
    //Delete ex
    $("#delete_expense"+id).on("click", handleDeleteExpense);
}

/**** END RESTFUL CLIENT****/


/**** BUTTON HANDLERS ****/

//User Handlers

function handleCreateUser(event){
    if (DEBUG) {
        console.log ("Triggered handleCreateUser")
    }
    var data = [$("#firstname_add").val(),
        $("#nickname_add").val(),
        $("#email_add").val(),
        $("#gender_add").val(),
        $("#birthday_add").val(),
        $("#password_add").val()];

    for(var i = 0; i < data.length; ++i){
        if(data[i] == ""){
            alert ("Could not create new user, some field is missing");
            return false;
        }
    }
    var envelope={'template':{
        'data':[]
    }};
    var userData = {};
    userData.name = "firstname";
    userData.value = data[0];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "nickname";
    userData.value = data[1];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "email";
    userData.value = data[2];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "gender";
    userData.value = data[3];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "birthday";
    userData.value = data[4];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "password";
    userData.value = data[5];
    envelope.template.data.push(userData);

    var url = "/accounting/api/users/";
    addUser(url, envelope);
    return false; //Avoid executing the default submit
}

function handleEditUser(event) {
    if (DEBUG) {
        console.log ("Triggered handleEdit")
    }
    event.preventDefault();

    var fn = $("#firstname_edit").val();
    var gender = $("#gender_edit").val();
    var birthday = $("#birthday_edit").val();
    var email = $("#email_edit").val();
    var balance = $("#balance_edit").val();

    if(fn == "") {    fn = $("#name").text();}
    if(gender == ""){ gender = $("#gender").text();}
    if(birthday == ""){ birthday = $("#birthday").text();}
    if(email == ""){ email = $("#email").text().split(" ")[1];}
    if(balance == ""){ balance = $("#balance").text().split(" ")[1];}

    var envelope={'template':{
        'data':[]
    }};
    var userData = {};
    userData.name = "gender";
    userData.value = gender;
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "birthday";
    userData.value = birthday;
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "email";
    userData.value = email;
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "userid";
    userData.value = currentUserId;
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "firstname";
    userData.value = fn;
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "balance";
    userData.value = balance;
    envelope.template.data.push(userData);

    var url = "/accounting/api/users/"+getQueryVariable("nickname")+"/";
    editUser(url, envelope);
    $("#edit_user_form").modal('hide');
    return false; //Avoid executing the default submit
}

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

//Income Handlers

function handleCreateIncome(event){
    if (DEBUG) {
        console.log ("Triggered handleIncomeUser")
    }
    var data = [$("#source_income").val(),
        $("#amount_income").val(),
        $("#date_income").val(),
        $("#description_income").val()];

    for(var i = 0; i < data.length; ++i){
        if(data[i] == ""){
            alert ("Could not create new income, some field is missing");
            return false;
        }
    }
    var envelope={'template':{
        'data':[]
    }};
    var userData = {};
    userData.name = "source";
    userData.value = data[0];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "amount";
    userData.value = data[1];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "date";
    userData.value = data[2];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "description";
    userData.value = data[3];
    envelope.template.data.push(userData);

    var url = "/accounting/api/user/"+currentUserId+"/incomes/";
    addIncome(url, envelope);
    return false; //Avoid executing the default submit
}

function handleDeleteIncome(event){
    if (DEBUG) {
        console.log ("Triggered handleDeleteIncome")
    }
    var id = event.currentTarget.innerHTML.split(" ")[1];
    var url = "/accounting/api/incomes/"+id+"/";
    deleteIncome(url);
    //reload
}


//Expense Handlers


function handleCreateExpense(Event){
    if (DEBUG) {
        console.log ("Triggered handleExpenseUser")
    }
    var data = [$("#source_expense").val(),
        $("#amount_expense").val(),
        $("#date_expense").val(),
        $("#description_expense").val()];

    for(var i = 0; i < data.length; ++i){
        if(data[i] == ""){
            alert ("Could not create new expense, some field is missing");
            return false;
        }
    }
    var envelope={'template':{
        'data':[]
    }};
    var userData = {};
    userData.name = "source";
    userData.value = data[0];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "amount";
    userData.value = data[1];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "date";
    userData.value = data[2];
    envelope.template.data.push(userData);
    userData = {};
    userData.name = "description";
    userData.value = data[3];
    envelope.template.data.push(userData);

    var url = "/accounting/api/user/"+currentUserId+"/expenses/";
    addIncome(url, envelope);
    return false; //Avoid executing the default submit
}

function handleDeleteExpense(event){
    if (DEBUG) {
        console.log ("Triggered handleDeleteExpense")
    }
    var id = event.currentTarget.innerHTML.split(" ")[1];
    var url = "/accounting/api/expenses/"+id+"/";
    deleteExpense(url);
    //reload
}

/**** END BUTTON HANDLERS ****/

/*** START ON LOAD ***/
//This method is executed when the webpage is loaded.
$(function(){

	//The handlers are:
    //Create user button
    $("#add_user").on("click", handleCreateUser);
    //Delete user button
    $("#delete_user_list").on("click", handleDeleteUserList);
    //Edit user button
    $("#edit_user_btn").on("click", handleEditUser);
    //Add income button
    $("#add_income").on("click", handleCreateIncome);
    //Add expense button
    $("#add_expense").on("click", handleCreateExpense);
	// Direct and delegated events from http://api.jquery.com/on/

	//Retrieve list of users from the server
    ENTRYPOINT = "/accounting/api/users/"+getQueryVariable("nickname")+"/";
	getUser(ENTRYPOINT);
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