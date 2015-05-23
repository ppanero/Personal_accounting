
/**** START CONSTANTS****/
//True or False
var DEBUG = true,
COLLECTIONJSON = "application/vnd.collection+json",
HAL = "application/hal+json",
FORUM_USER_PROFILE = "http://atlassian.virtues.fi:8090/display/PWP/Exercise+4#Exercise4-Forum_User",
FORUM_MESSAGE_PROFILE = "http://atlassian.virtues.fi:8090/display/PWP/Exercise+4#Exercise4-Forum_Message",
DEFAULT_DATATYPE = "json",
ENTRYPOINT = "/forum/api/users/" //Entry point is getUsers()
/**** END CONSTANTS****/

/**** START RESTFUL CLIENT****/
/*
getUsers is the entrypoint of the application.

Sends an AJAX request to retrive the list of all the users of the application
ONSUCCESS=> Show users in the UI list. It uses appendUserToList for that purpose. 
The list contains the url of the users.
ONERROR => Show an alert to the user
*/
function getUsers() {
	var apiurl = ENTRYPOINT;
	return $.ajax({
		url: apiurl,
		dataType:DEFAULT_DATATYPE
	}).always(function(){
		//Remove old list of users, clear the form data hide the content information(no selected)
		$("#user_list").empty();
		$("#mainContent").hide();

	}).done(function (data, textStatus, jqXHR){
		if (DEBUG) {
			console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
		}
		//Extract the users
    	var users = data.collection.items;
		for (var i=0; i < users.length; i++){
			var user = users[i];
			//Extract the nickname by getting the data values. Once obtained
			// the nickname use the method appendUserToList to show the user
			// information in the UI.
			//Data format example:
			//  [ { "name" : "nickname", "value" : "Mystery" },
			//    { "name" : "registrationdate", "value" : "2014-10-12" } ]
			var user_data = user.data;
			for (var j=0; j<user_data.length;j++){
				if (user_data[j].name=="nickname"){
					appendUserToList(user.href, user_data[j].value);
				}			
			} 
		}
		//Set the href of #addUser for creating a new user
		setNewUserUrl(data.collection.href)
	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
		}
		//Inform user about the error using an alert message.
		alert ("Could not fetch the list of users.  Please, try again");
	});
}

/*
Sends an AJAX request to retrive the template to create a new user.
	ONSUCCESS=> Show in #mainContent the form to create a new user (create_user_form).
	            a)The necessary input names are read from the response template element.
	            b)The Form is created using the helper methods createFormFromTemplate.
	            c)The Form is added using the helper method showNewUserForm 
	ONERROR => a)Show an alert to the user 
	           b) Go back to initial state by calling deselect user. 
*/
function getUsersForm(apiurl) {
	return $.ajax({
		url: apiurl,
		dataType:DEFAULT_DATATYPE
	}).done(function (data, textStatus, jqXHR){
		if (DEBUG) {
			console.log ("RECEIVED RESPONSE GETUSERSFORM: data:",data,"; textStatus:",textStatus)
		}
		$form = createFormFromTemplate (data.collection.href, 
			                            data.collection.template,
			                            "create_user_form","Create",
			                            handleCreateUser);
 		showNewUserForm($form);
	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR GETUSERSFORM: textStatus:",textStatus, ";error:",errorThrown)
		}
		//Inform user about the error using an alert message.
		alert ("Could not create a link to create new users.  Please, try again");
		deselectUser()
	});
}
/*
Sends an AJAX request to retrieve information related to a user(Resource name = User. See Appendix1)
INPUT: apiurl => The URL of the target user

ONSUCCESS => 
             a)Extract basic user information (nickname and registereddate)
               from the response and show it in the #user_public_form
             b)Add the url of the current user (self) to the action attribute
               of user_public_form. In that way we can Delete the current user
               by pressing #deleteUser button.  
             c)Extract the URL of the user restricted_profile (User_restricted resource)
               and user history (History resource). 
    		 d)Get the previous resources in parallel by calling getRestrictedProfile()
    		   and getUserHistory()
    		 e) The handlers of the previous methods will show the required
    		    information to the user. 
ONERROR =>   a)Alert the user
             b)Unselect the user from the list and go back to initial state 
*/

function getUser(apiurl) {
	return $.ajax({
		url: apiurl,
		dataType:DEFAULT_DATATYPE
		//headers: {"Authorization":"admin"}
	}).done(function (data, textStatus, jqXHR){
		if (DEBUG) {
			console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
		}
		
		//Extract user information
		var user_links = data._links;
		//Extracts urls
		var private_profile_url = user_links["restricted-data"].href;
		var messages_url = user_links.messages.href; 
        var self = user_links.self.href;

		//Purge and show the existingUserData div.
		showExistingUserData();

		//Fill basic information from the user_public_form and set the action
		//For the delete button.
		$("#nickname").val(data.nickname);
		$("#registrationdate").val(getDate(data.registrationdate));
		$("form#user_public_form").attr("action",self);


		//Fill the user profile with restricted user profile. This method
		// Will call also to the list of messages.
		getRestrictedProfile(private_profile_url);
		//Get the history link and ask for history.
		getUserHistory(messages_url);

	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
		}
		//Show an alert informing that I cannot get info from the user.
		alert ("Cannot extract information about this user from the forum service.")
		//Deselect the user from the list.
		deselectUser()
	});
}


/*
Sends an AJAX request to retrieve the restricted profile information
(Resource name = User_restricted. See Appendix1)
It must be an authorized request so it must include Authorization header with value "admin".
INPUT: apiurl => The URL of the public profile
ONSUCCESS => 
	a)Create and fill the form (#user_restricted_form) with the information received on 
	  the data parameter.
	  a.1) Call the method createFormFromTemplate in order to create such form.
	       The template is obtained from the response data. 
	  a.2) Fill it with with the properties received in the respnse data. 
	       Accordding to appendix 1 a template of a restricted profile have 
	       the following properties: 
			* "address"
            * "birthday"
            * "email"
            * "familyName"
            * "gender"
            * "givenName"
            * "website"
            * "telephone"
            * "skype"
            * "image"
       a.3) Append the form to the #userRestrictedInfo container
ONERROR =>
  	a)Show an alert informing the restricted profile could not be retrieved and 
  	  that the data shown in the screen is not complete.
    b)Unselect current user and go to initial state by calling deselectUser .
*/
function getRestrictedProfile(apiurl){
	return $.ajax({
		url: apiurl,
		dataType:DEFAULT_DATATYPE, 
		headers: {"Authorization":"admin"}
	}).done(function (data, textStatus, jqXHR){
		if (DEBUG) {
		console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
		}
		//Create a form with the template values.
		var template = data.template;
		var edit_url = data._links.edit.href;
		$form = createFormFromTemplate(edit_url, template, "user_restricted_form", "Edit", handleEditUser)
		//Fill the form with right values. Those can later be edited.
		
		//The following code commented does not make use of fully hypermedia
		//characteristics but it is also valid.
		/*$form.children("input[name=birthday]").val(data.birthday);
		$form.children("input[name=email]").val(data.email);
		$form.children("input[name=familyName]").val(data.familyName);
		$form.children("input[name=gender]").val(data.gender);
		$form.children("input[name=givenName]").val(data.givenName);

		$form.children("input[name=image]").val(data.image);
		$form.children("input[name=telephone]").val(data.telephone);
		$form.children("input[name=website]").val(data.website);
		$form.children("input[name=skype]").val(data.skype);*/
        
        //Use the template in order to extract the required values. 
		$inputs= $form.children("input");
		$inputs.each(function(){
			$(this).val(data[this.name])
		});
		//Add the for to userRestrictedInfo
		$("#userRestrictedInfo").append($form);
		
	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
		}
		//Show an alert informing that I cannot get info from the user.
		alert ("Cannot extract all the information about this user from the server");
		deselectUser();
	});
}
/*
Sends an AJAX request to retrieve information related to user history.
INPUT: apiurl => The URL of the History resource
ONSUCCESS => 
	a)Check the number of messages received (data.items) and add this value to the #messageNumber span element.
	b)Iterate through all messages. For each message in the history, call the function getMessage(messageurl). You
	  can extract the url of each message from the response object.
ONERROR =>
  	a)Show an alert informing the user that the target user history could not be retrieved
  	b)Deselect current user and go to the initial state by calling the deselectUser() method.
  	
*/
function getUserHistory(apiurl){
	//TODO 3: Send the AJAX to retrieve the history information. Do not implement the handlers yet, just show some DEBUG text in the console. 
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE
	//TODO 4: Implement the handlers successful and failures responses accordding to the function documentation.
    }).done(function (data, textStatus, jqXHR){
		if (DEBUG) {
			console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
		}
        //Extract the users
        var messages = data.collection.items;
        for (var i=0; i < messages.length; i++){
            var url = messages[i].href;
            var message = getMessage(url);
            //Extract the healine by getting the data values. Once obtained
            // the headline use the method appendMessageToList to show the user
            // information in the UI.
            //Data format example:
            //{ "name" : "headline", "value" : "CSS: Margin problems with IE" },
            var message_data = message.data;
            for (var j=0; j<message_data.length;j++){
                var headline = "";
                var body = ""
                if (message_data[j].name=="headline"){
                    headline = message_data[j];
                }
                if(message_data[j].name=="articleBody"){
                    body = message_data[j];
                }
                appendMessageToList(url,headline,body);
            }
        }
	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
		}
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not get user's message history");
	});
}
/*
Sends an AJAX request to create a new user (POST).
INPUT: apiurl => The URL of the new User
	   userData => The template object to be returned as a Javascript object
	   nickname => The nickname of the user.
ONSUCCESS => 
	a)Show an alert informing the user that the user information has been modified
	b)Append the user to the list of users (call appendUserToList)
	  * The url of the resource is in the Location header
	  * appendUserToList returns the li element that has been added.
	c)Make a click() on the added li element. To show the information.
ONERROR =>
  	a)Show an alert informing the user that the new information was not stored in the databse
  	
*/
function addUser(apiurl, userData, nickname){
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
		//Add the user to the list and load it.
		$user = appendUserToList(jqXHR.getResponseHeader("Location"),nickname);
		$user.children("a").click();

	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
		}
		alert ("Could not create new user");
	});
}

/*
Sends an AJAX request to modify the restricted profile of a user (PUT)
INPUT: apiurl => The URL of the restricted profile to modify
	   template => The Javascript object containing the Collecton+JSON template
	   with the existing data. 
	   Check the format from Appendix1 (Resource name = User_restricted) 
ONSUCCESS => 
	a)Show an alert informing the user that the user information has been modified
ONERROR =>
  	a)Show an alert informing the user that the new information was not stored in the databse
  	b)Unselect current user and go to the initial state by calling deselectUser
  	
*/
function editRestrictedUserProfile(apiurl, template) {
	$.ajax({
	//TODO 3: Send an AJAX request to modify the restricted profile of a user
		// Do not implement the handlers yet, just show some DEBUG text in the console.
		// Check addUser for some hints.
		// Do not forget to include:
		//   * To modify a User_restricted resource you must use the PUT method.
		//   * The header "Authorization with value admin"
		//   * The contentType is CollectionJSON+";"+FORUM_USERPROFILE
		//   * You should not processData (processData:false)
		//   * The data you want to send in the entity body is obtained by
		//       appliying the method JSON.stringify() to the given template.
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
/*
Sends an AJAX request to delete an user from the system (DELETE)
INPUT: apiurl => The URL of the user to remove

ONSUCCESS => 
	a)Show an alert informing the user that the user has been deleted
	b)Reload the list of users: getUsers().
ONERROR =>
  	a)Show an alert informing the user could not been deleted
*/
function deleteUser(apiurl) {
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
		//Update the list of users from the server.
		getUsers();

	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
		}
		alert ("The user could not be deleted from the database");
	});
}
/*
Sends an AJAX request to retrive a message resource (GET)
ONSUCCESS=> a)Create a new form of class .message with the content of this response
	  a.1) Call the helper method appendMessageToList
	  a.2) Get the title and the body of the message from the HTTP response 
ONERROR => Show an alert to the user
*/
function getMessage(apiurl) {
	$.ajax({
		url: apiurl,
		dataType:DEFAULT_DATATYPE
	}).done(function (data, textStatus, jqXHR){
		if (DEBUG) {
			console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
		}
		var message_url = data._links.self.href;
		var headline = data.headline;
		var articleBody =  data.articleBody;
		appendMessageToList(message_url, headline, articleBody);

	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
		}
		alert("Cannot get information from message: "+ apiurl);
	});
}
/*
Sends an AJAX request to remove a message resource (DELETE)
ONSUCCESS=>
      a) Inform the user with an alert. 
      b) Go to the initial state by calling the reloadUserData function.
ONERROR => Show an alert to the user
*/
function deleteMessage(apiurl){
	$.ajax({
	//TODO 3: Send an AJAX request to remove the current message
		// Do not implement the handlers yet, just show some DEBUG text in the console.
		// You just need to send a $.ajax request of type "DELETE". No extra parameters
		//are required.
    url: apiurl,
    type: "DELETE",
    dataType:DEFAULT_DATATYPE
    //TODO 4
       //Implemente the handlers following the instructions from the function documentation.
	}).done(function (data, textStatus, jqXHR){
		if (DEBUG) {
			console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus)
		}
        alert ("The message has been deleted from the database");
        //Update the list of users from the server.
        getUserHistory();
	}).fail(function (jqXHR, textStatus, errorThrown){
		if (DEBUG) {
			console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown)
		}
        //The behaviour upon failure is not defined. Left with log message
        alert ("Could not delete message");
	});
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

	var userurl = $(this).closest("form").attr("action");
	deleteUser(userurl);
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

/**** UI HELPERS ****/
/*
Add a new li element in the #user_list using the information received as parameter
	PARAMETERS: nickname => nickname of the new user shown in the screen. 
	            url=> url of the new user. 
				
*/
function appendUserToList(url, nickname) {
	var $user = $('<li>').html('<a class= "user_link" href="'+url+'">'+nickname+'</a>');
	//Add to the user list
	$("#user_list").append($user);
	return $user;
}
/*
Sets the url to add a new user to the list.
*/
function setNewUserUrl(url){
	console.log("NEW URL, ", url)
   $("#addUser").attr("href", url);
}
/*
Creates a form with the values coming from the template.

INPUT:
 * url=Value that will be writtn in the action attribute.
 * template=Collection+JSON template which contains all the attributes to be shown.
 * id = unique id assigned to the form.
 * button_name = the text written on associated button. It can be null;
 * handler= function executed when the button is pressed. If button_name is null
   it must be null.

 OUTPUT:
  The form as a jquery element.
*/
function createFormFromTemplate(url,template,id,button_name,handler){
	$form=$('<form></form>');
	$form.attr("id",id);
	$form.attr("action",url);
	if (template.data) {
		for (var i =0; i<template.data.length; i++){
			var name = template.data[i].name;
			var id = name+"_id";
			var value = template.data[i].value;
			var prompt = template.data[i].prompt;
			var required = template.data[i].required;
			$input = $('<input type="text"></input>');
			$input.addClass("editable");
			$input.attr('name',name);
			$input.attr('id',id);
			if(value){
				$input.attr('value', value);
			}
			if(prompt){
				$input.attr('placeholder', prompt);
			}
			if(required){
				$input.prop('required',true);
			}
			$label_for = $('<label></label>')
			$label_for.attr("for",id);
			$label_for.text(name);
			$form.append($label_for);
			$form.append($input);
		}
		if (button_name) { 
			$button = $('<button type="submit"></button>');
			$button.attr("value",button_name);
			$button.text(button_name);
			$form.append($button);
			$form.submit(handler);
		}
	}
	return $form;
}

/*

Serialize the input values from a given form into a Collection+JSON template.

INPUT:
A form jquery object. The input of the form contains the value to be extracted.

OUPUT:
A Javascript object containing each one of the inputs of the form serialized
following  the Collection+JSON template format.
*/
function serializeFormTemplate($form){
	var envelope={'template':{
								'data':[]
	}};
	// get all the inputs into an array.
    var $inputs = $form.children("input");
    $inputs.each(function(){
    	var _data = {};
    	_data.name = this.name;
    	_data.value = $(this).val();
    	envelope.template.data.push(_data);
    });
    return envelope;

}

/*
Add a new .message element to the #list in #messages
	PARAMETERS: url=> url of the new message. It is stored in the action attribute of the corresponding form
				tite=>The title of the message
				body=> The body of the message.
*/
function appendMessageToList(url, title, body) {
	/* WE have to build the following HTML document
		<div class='article'>  
			<form action='#'>  
				<header class='messageIntro'>  
					<span class='messageTopic'></span> 
				</header>
				<p class='messageText'></p>  
	    		<div class='messageTools' >  
					<p class='commands'>
					    <input type='button' class='saveMessage' value='Save' /><input id='deleteMessage' type='button' value='Delete'/>
					</p> 
				</div>
			</form>
		</div>*/
	var $message = $("<div>").addClass('message').html(""+
						"<form action='"+url+"'>"+  
							"<header class='messageIntro'>"+ 
								"<span class='messageTopic'>"+title+"</span>"+ 
							"</header>"+
							"<p class='messageText'>"+body+"</p>"+ 
				    		"<div class='messageTools' >"+  
								"<span class='commands'>"+
								"<input id='deleteMessage' type='button' value='Delete'/>"+
								"</span>"+ 
							"</div>"+
						"</form>"
					);
	//Append to list
	$("#messages #list").append($message);		
}

/*Helper method to show the ExistingUserData. It purges the old data.

*/
function showExistingUserData() {
	//Be sure that mainContent is shown
	$("#mainContent").show();
	//Remove the action in the Delete button
	$("form#user_public_form").attr('action','#');
	//Empty the nickname and registration data
	$("form#user_public_form")[0].reset();
	//Remove all data of the user
	$("#userRestrictedInfo").empty();
	//Clean the message list
	$("#messages #list").empty();
	//Reset the number of messages
	$("#messagesNumber").text("");
	//Hide the newUserData if it was shown
	$("#newUserData").hide();
	//Show existingUserData
	$("#existingUserData").show();
}
/*
Helper method to purge and show the newUserData form.
*/
function showNewUserForm ($form) {
	//Remove selected users in the sidebar
	deselectUser();
	//Be sure that mainContent is shown
	$("#mainContent").show();
	//Remove data from previously created users
	$("#newUserData").empty();
	//Add the new form
	$("#newUserData").append($form);
	//Hide existingUserData div
    $("#existingUserData").hide();
    //Show the div with the new form.
    $("#newUserData").show();
}
/**
Helper method that unselect any user from the User_list and go back to the 
initial state by hiding the "#mainContent". 
**/
function deselectUser() {
	$("#user_list li.selected").removeClass("selected");
	$("#mainContent").hide();
}

/*
Helper method to reloadUserData. Internally it makes click on the href of the 
selected user.
*/
function reloadUserData() {
	var selected = $("#user_list li.selected a");
	selected.click();
}

/**
Transform a date given in a UNIX timestamp into a more user friendly string.
**/
function getDate(timestamp){
	// create a new javascript Date object based on the timestamp
	// multiplied by 1000 so that the argument is in milliseconds, not seconds
	var date = new Date(timestamp*1000);
	// hours part from the timestamp
	var hours = date.getHours();
	// minutes part from the timestamp
	var minutes = date.getMinutes();
	// seconds part from the timestamp
	var seconds = date.getSeconds();

	var day = date.getDate();

	var month = date.getMonth()+1;

	var year = date.getFullYear()

	// will display time in 10:30:23 format
	return day+"."+month+"."+year+ " at "+ hours + ':' + minutes + ':' + seconds;
}

/*** END UI HELPERS***/

/*** START ON LOAD ***/
//This method is executed when the webpage is loaded.
$(function(){

	//TODO 1: Add corresponding click handler to #deleteUser and #addUser buttons.
	//The handlers are:
	// #deleteUser -> handleDeleteUser
    $("#deleteUser").on("click", handleDeleteUser);
	// #addUser -> handleCreateUserForm
    $("#addUser").on("click", handleCreateUserForm);
	// Check http://api.jquery.com/on/ for more help.

	//TODO 1: Add corresponding click handlers for #deleteMessage button and
	// anchor elements with class .user_link from #user_list
	//Since these elements are generated programmatically
	// (they are not in the initial HTML code), you must use delegated events.
	//Recommend delegated elements are #messages for #deleteMessage button and
	// #user_list for  "li a.user_link"
	//The handlers are:
	// #deleteMessage => handleDeleteMessage
    $("#messages").on("click", "div div form div span input", handleDeleteMessage);
	// li a.user_link => handleGetUser
    $("#user_list").on("click", "li a", handleGetUser);
	// Direct and delegated events from http://api.jquery.com/on/

	//Retrieve list of users from the server
	getUsers();
})
/*** END ON LOAD**/