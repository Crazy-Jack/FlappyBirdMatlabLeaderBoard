$(document).ready(function () {
    $.fn.extend({
        numOnly: function (num) {
            $(this).on("keydown", function (e) {
                var arr = [8, 16, 17, 20, 35, 36, 37, 38, 39, 40, 45, 46];
                // Allow number
                for (var t = 48; t <= 57; t++) {
                    arr.push(t);
                }

                if (jQuery.inArray(event.which, arr) === -1) {
                    event.preventDefault();
                }
                if ($(this).val().length > num) {
                    $(this).val($(this).val().substr(0, num));
                }
            });
        }
    });
    

    function deleteSubmission(md5) {
	    // delete submission for md5
	    console.log("this")
	    console.log(this)
	    console.log("delete " + md5);
	    
	    $.getJSON("/tools/delete_md5/", {'md5': md5}).done(function (delete_flag) {
		query_user_table();
		console.log(delete_flag);
	    	}).fail();

	};
    function query_user_table() {
	
        $.getJSON("/tools/get_user_data/", {}).done(function (querys) {
            console.log("querys")
            console.log(querys)
                var table_html = `
                <table id="usertable">
                    <tr>
                        <th style="width: 5%;text-align: center;">Manage</th>
                        <th style="width: 5%;text-align: center;">Category</th>
                        
                        <th style="width: 10%;text-align: center;">Update Time</th>

                        <th style="width: 10%;text-align: center;">Best Score </th>

                        <th style="width: 10%;text-align: center;">Train Time (s)</th>

                        <th style="width: 10%;text-align: center;">No. Neurons</th>
                        <th style="width: 10%;text-align: center;">Submission MD5</th>
                        <th style="width: 10%;text-align: center;"> Video url </th>

                    </tr>`;
            for (var i in querys) {
                table_html += `<tr><td style="width: 5%;text-align: center;word-wrap: break-word;"><div id="row_${i}" class="clickdelete" value="${querys[i].md5}"><i class="fa fa-trash clickdelete"></i></div></td>`	
                table_html += `<td style="width: 5%;text-align: center;word-wrap: break-word;">${querys[i].category} </td>`	
                table_html += `<td style="width: 10%;text-align: center;word-wrap: break-word;">${querys[i].submission_time}</td>`	
                table_html += `<td style="width: 10%;text-align: center;word-wrap: break-word;">${querys[i].best_score}</td>`	
                table_html += `<td style="width: 10%;text-align: center;word-wrap: break-word;">${querys[i].train_time}</td>`
                table_html += `<td style="width: 10%;text-align: center;word-wrap: break-word;">${querys[i].num_nn}</td>`		
                table_html += `<td style="width: 10%;text-align: center;word-wrap: break-word;">${querys[i].md5}</td>`		
                table_html += `<td style="width: 10%;text-align: center;word-wrap: break-word;"><a href="https://www.youtube.com/watch?v=${querys[i].youtube_url}" target="_blank">https://www.youtube.com/watch?v=${querys[i].youtube_url}</a></td>`		
                
                // table_html += `<td style="width: 70%;text-align: center;word-wrap: break-word;"> <iframe width="560" height="315" src="https://www.youtube.com/embed/${querys[i].youtube_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></td></tr>`
                
            };
            
            table_html += `</table>`;
            $(`#usertable`).html(table_html)
	    console.log(querys);
	    for (var i in querys) {

		document.getElementById(`row_${i}`).addEventListener("click", function () {
			deleteSubmission(this.getAttribute('value'));	
		}, false);

	    }
        });
    };
	query_user_table();
    
    function finishProcess(md5) {
        $('#processtip').text('Submission Completed!');	// refresh the table
	// another ajax to /tools/get_user_data/ (returns a qeury table)


	query_user_table();
	
    }

    //console.log("running");
    $('#myfile').change(function () {
        $("#processtip").text('');
        var a = $('#myfile').val().toString().split('\\'),
            fileSize = document.getElementById('myfile').files[0].size,
            fileSize_num = Math.round(100*fileSize/1024)/100 == 0 ? 0.01: Math.round(100*fileSize/1024)/100;
            displaySize = fileSize_num >= 1024 ? Math.round(100*fileSize_num/1024)/100 + 'MB ' : fileSize_num+'KB ';
        //console.log(a);
        $('#filename').text(displaySize + a[a.length - 1]);
        if ($('#myfile').val() !== "") {
            $('#cancel').show().click(function () {
                $('#filename').text('');
                $('#cancel').hide();
                $('#processtip').children('p').remove();
                $('#myfile').val('');
                //console.log('Hello', $('#myfile').val());
                $('#submit').removeAttr('disabled');
            });
        }
        //console.log("File size: ", document.getElementById('myfile').files[0].size);
        if (fileSize >= 30 * 1024 * 1024) {
            $('#submit').prop('disabled', true);
            $('#processtip').append('<p>File size are limited to 30MB. Try following steps to reduce file size: </p>').css("color", "#000");
            $('#processtip').append('<p> 1. Filter your Data</p>' + '<p> 2. Remove useless info</p>' + '<p> 3. Contact us for help</p>').css("color", "#000");
        }
    });

    $('.textarea').bind('input propertychange', function () {
        if ($('.textarea').text() !== "") {
            $('#uploadlabel').hide();
            $('#submit').hide();
        } else {
            $('#uploadlabel').show();
            $('#submit').show();
        }
    });

    $('#denvalue').numOnly(2);

    $('#denvalue').change(function () {
        if (parseInt($('#denvalue').val()) > 100) {
            $('#denvalue').val('100');
        }
        if (parseInt($('#denvalue').val()) == 0) {
            $('#denvalue').val('1');
        }
    });

    //$("div#drop-select-file").dropzone({ url: "/tools/upload/" });

    $('#submit').click(function (e) {
        e.preventDefault();
        //e.stopPropagation();
        if ($('#myfile').val() === "") {
            $('#processtip').text('Please choose a file to upload.').css("color", "#CB4042");
        } else if ($('#django_username').val() == "AnonymousUser") {
            $('#processtip').text('Please Login First.').css("color", "#CB4042");
        } else {

            var formdata = new FormData(),
                category_val = $("#category").val(),
                youtube_url = $("#youtube").val(),
                num_nn = $("#num_nn").val(),
                parameters = {
                    "category": category_val,
                    "youtube_url": youtube_url,
                    "num_nn": num_nn,
                };
            
                console.log(parameters);

            formdata.append('file', document.getElementById('myfile').files[0]);
            formdata.append('parameters', JSON.stringify(parameters));
            //console.log(JSON.stringify(parameters));
            //console.log(parameters);
            var ajaxParameters = {
                url: '/tools/submit/',
                type: 'POST',
                cache: false,
                dataType: "json",
                data: formdata,
                processData: false,
                contentType: false,
                timeout: 5000000000,
            };

	    //$('#submit').text('✓ Submitted').prop('disabled', true);
            $('#cancel').hide();
            
            $('#processtip').after('<div class="lds-roller d-inline-block"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div><p class="d-inine-block" id="upload-text">Uploading...</p>');
           

            $.ajax(ajaxParameters)
                .done(
                    function (reportID) {
                        var md5 = reportID[0].md5,
                            status = reportID[0].save_status;
                            error_message = reportID[0].error;

                        if (status === false) {
                            $('.lds-roller').remove();
                            $('#upload-text').remove();
                            $('#processtip').html('<p>Processing Failed! Error: ' + error_message + '. Please <a id="refresher" onclick="location.reload()"><i>refresh</i><i class="fas fa-redo-alt ml-1"></i></a></p>');
                            $('#refresher').hover(function(){
                                $('#refresher').css({'cursor':'pointer', 'color': '#fed136'});
                            },
                            function(){
                                $('#refresher').css('color', 'black');
                            });
                        }
                        else if (status === true) {
                            $('.lds-roller').remove();
                            $('#upload-text').remove();
                            finishProcess(md5);
                           
                        }
                      
                    }).fail(
                    function () {
                        $('.lds-roller').remove();
                        $('#upload-text').remove();
                        $('#processtip').html('<p>Server timeout, please <a id="refresher" onclick="location.reload()"><i>refresh</i><i class="fas fa-redo-alt ml-1"></i></a></p>');
                        $('#refresher').hover(function(){
                            $('#refresher').css({'cursor':'pointer', 'color': '#fed136'});
                        },
                        function(){
                            $('#refresher').css('color', 'black');
                        });
                        $('#submit').text('Submit');
                    }
                );
        }
    })


});
