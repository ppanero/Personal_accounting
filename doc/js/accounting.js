$( document ).ready(function() {

    // Sistemita de alertas
    function launchAlert(value, message) {
        if(parseInt(value) == 1) { // SUCCESS ALERT
            $(".alerts").append('<p class="bg-success message">'+message+'</p>');
            setTimeout(function() {
                $(".alerts").html('');
            }, 3000);
        } else if(parseInt(value) == 0) { // INFO
            $(".alerts").append('<p class="bg-primary message">'+message+'</p>');
            setTimeout(function() {
                $(".alerts").html('');
            }, 3000);
        }else if(parseInt(value) == -1) { // ERROR ALERT
            $(".alerts").append('<p class="bg-danger message">'+message+'</p>');
            setTimeout(function() {
                $(".alerts").html('');
            }, 3000);
        }

    }

    ////////////////////////////////// HOME
    // Delete
    $(".delete").click(function(){
        var id = $(this).parent().attr('id');
        if((id.indexOf('law') >= 0)) {
            deleteLaw($(this));
        }else if(id.indexOf('propuesta') >= 0) {
            deletePropuesta($(this));
        }else if(id.indexOf('enmienda') >= 0) {
            deleteEnmienda($(this));
        }else
            launchAlert(-1,"ERROR, ¿Qué debería borrar?");
    });
    // Delete Law
    function deleteLaw(element) {
        var ask = confirm("¿Seguro que quiere borrar la Ley?");
        if(ask) {
            var id = element.parent().attr("id").split('-')[1];
            var ok = deleteLawAux(id);
            if(parseInt(ok) > 0) {
                element.parent().remove();
                launchAlert(1, "La ley ha sido eliminada con éxito");
            }
            else
                launchAlert(-1, "No se ha podido eliminar la ley");
        }
    }

    function deleteLawAux(id) {
        var result="";
        $.ajax({
            url:"requestHandler.php?subject=laws&action=delete&id="+id,
            async: false,
            success:function(data) {
                result = data;
            }
        });
        return result;
    }

    // Delete Propuesta
    function deletePropuesta(element) {
        var ask = confirm("¿Seguro que quiere borrar la Propuesta?");
        if(ask) {
            var id = element.parent().attr("id").split('-')[1];
            var ok = deletePropuestaAux(id);
            if(parseInt(ok) > 0) {
                element.parent().remove();
                launchAlert(1, "La propuesta ha sido eliminada con éxito");
            }
            else
                launchAlert(-1, "No se ha podido eliminar la propuesta");
        }
    }

    function deletePropuestaAux(id) {
        var result="";
        $.ajax({
            url:"requestHandler.php?subject=propuestas&action=delete&id="+id,
            async: false,
            success:function(data) {
                result = data;
            }
        });
        return result;
    }

    // Delete Enmienda
    function deleteEnmienda(element) {
        var ask = confirm("¿Seguro que quiere borrar la Enmienda?");
        if(ask) {
            var id = element.parent().attr("id").split('-')[1];
            var ok = deleteEnmiendaAux(id);
            if(parseInt(ok) > 0) {
                element.parent().remove();
                launchAlert(1, "La enmienda ha sido eliminada con éxito");
            }
            else
                launchAlert(-1, "No se ha podido eliminar la enmienda");
        }
    }

    function deleteEnmiendaAux(id) {
        var result="";
        $.ajax({
            url:"requestHandler.php?subject=enmiendas&action=delete&id="+id,
            async: false,
            success:function(data) {
                result = data;
            }
        });
        return result;
    }

    // Edit Law
    $(".edit").click(function(){
        var id = $(this).parent().attr("id").split('-')[1];
        alert("edit law " + id);
    });

    // Validacion Usuario

    $("#username").change(function(){
        var url="comprobarUsuario.php?user=" + $("#username").val();
        $.get(url,usuarioExiste);

    });

    function usuarioExiste(data,status) {
        if(data == "disponible") {
            $("#statusOkUser").show(); // Mostrar icono verde
            $("#statusNoUser").hide(); // Ocultar icono rojo 
        } else {
            $("#statusOkUser").hide(); // Ocultar icono verde 
            $("#statusNoUser").show(); // Mostrar icono rojo
        }
    }



});