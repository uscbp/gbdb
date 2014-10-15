var globalMarker;

function deleteInlineForm(prefix, idx){
    document.getElementById('id_'+prefix+'-'+idx+'-DELETE').value='on';
    document.getElementById(prefix+'-'+idx).style.display='none';
    return false;
}

function showPopup(windowName, width, height, href)
{
    if (href.indexOf('?') == -1)
        href += '?_popup=1';
    else
        href  += '&_popup=1';
    var win = window.open(href, windowName, 'height='+height+',width='+width+',resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function updateCircle()
{
    // Add circle overlay and bind to marker
    var circle = new google.maps.Circle({
        map: map,
        radius: 16093,    // 10 miles in metres
        fillColor: '#AA0000'
    });
    circle.bindTo('center', marker, 'position');
}

function getTRTag(idx)
{
    if(idx%2==0)
        return 'even_row';
    else
        return 'odd_row';
}

function populateLocation()
{
    var location_id=document.getElementById('id_saved_locations').value;
    var data={'id':location_id};
    var args={type:"GET", url:"/gbdb/saved_location/", data: data, complete: donePopulateLocation };
    $.ajax(args)
}

function donePopulateLocation(res, status)
{
    var txt = res.responseText;
    var data = eval('('+txt+')');
    if (status=="success")
    {
        document.getElementById('id_location_name').value=data.name;
        document.getElementById('id_location_0').value=data.latitude;
        document.getElementById('id_location_1').value=data.longitude;
        var center = new google.maps.LatLng(parseFloat(data.latitude), parseFloat(data.longitude));
        globalMarker.setPosition(center);
        map.setCenter(center);
        map.setZoom(5);
    }
}

function createSavedLocation()
{
    var name=document.getElementById('id_location_name').value;
    var latitude=document.getElementById('id_location_0').value;
    var longitude=document.getElementById('id_location_1').value;
    if(name.length>0 && latitude.length>0 && longitude.length>0)
    {
        var data={'name':name, 'latitude':latitude, 'longitude':longitude};
        var args={type:"POST", url:"/gbdb/saved_location/new/", data: data, complete: doneCreateSavedLocation };
        $.ajax(args);
    }
    return false;
}

function doneCreateSavedLocation(res, status)
{
    var txt = res.responseText;
    var data = eval('('+txt+')');
    if (status=="success")
    {
        alert('Location saved');
        var locElem=document.createElement('option');
        locElem.value=data.id;
        locElem.innerHTML=data.name;
        locElem.selected='selected';
        var selectElem=document.getElementById('id_saved_locations');
        selectElem.appendChild(locElem);
    }
    return false;
}

jQuery.fn.scrollTo = function(elem) {
    $(this).scrollTop($(this).scrollTop() - $(this).offset().top + $(elem).offset().top);
    return this;
};