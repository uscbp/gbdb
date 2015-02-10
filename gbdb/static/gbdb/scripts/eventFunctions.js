/**
 * Highlight event
 * @param idx - event index
 */
function highlightEvent(idx)
{
    $(document.getElementById('behavioral_event-' + idx)).css("border","5px solid #FF0");
}

/**
 * Highlight subevent
 * @param parentIdx - index of parent event
 * @param idx - index of  subevent
 */
function highlightSubEvent(parentIdx, idx)
{
    $(document.getElementById('sub_behavioral_event-' + parentIdx+'.'+idx)).css("border","5px solid #FF0");
}

/**
 * Unhighlight all events
 */
function unhighlightAllEvents()
{
    $('.behavioral_event').each(function(){
        $(this).css("border","5px solid transparent");
    });
}

/**
 * Unhighlight all subevents
 */
function unhighlightAllSubEvents()
{
    $('.sub_behavioral_event').each(function(){
        $(this).css("border","5px solid transparent");
    });
}

/**
 * Relabel all events assuming they've been inserted in the list in the correct order
 */
function relabelEvents()
{
    // Iterate through events
    $(document.getElementById('behavioral_events')).children("[id^=behavioral_event]").each(function(index){
        // Get index
        var eventIdx=parseInt(this.getElementsByClassName('behavioral_event-idx')[0].textContent);
        // Update label
        $(this.getElementsByClassName('behavioral_event-label')[0]).html('Behavioral Event '+(index+1).toString());
        // Update track label
        for(var i=0; i<periods.length; i++)
        {
            if(!('parentIdx' in periods[i].data) && periods[i].data.idx==eventIdx)
            {
                periods[i].data.label=(index+1).toString();
            }
        }
        relabelSubevents(eventIdx);
    });
}

/**
 * Relabel subevents
 * @param eventIdx - index of parent event
 */
function relabelSubevents(eventIdx)
{
    // Iterate through subevents
    $(document.getElementById('sub_behavioral_events_list-'+eventIdx)).children("[id^=sub_behavioral_event]").each(function(index){
        // Get parent event label
        var parentEventLabel='';
        for(var i=0; i<periods.length; i++)
        {
            if(!('parentIdx' in periods[i].data) && periods[i].data.idx==eventIdx)
            {
                parentEventLabel=periods[i].data.label;
                break;
            }
        }
        // Get subevent index
        var subeventIdx=parseInt(this.getElementsByClassName('sub_behavioral_event-idx')[0].textContent);
        // Update subevent label
        $(this.getElementsByClassName('sub_behavioral_event-label')[0]).html('Subevent '+parentEventLabel+'.'+(index+1).toString());
        // Update subevent track label
        for(var i=0; i<periods.length; i++)
        {
            if('parentIdx' in periods[i].data && periods[i].data.parentIdx==eventIdx && periods[i].data.idx==subeventIdx)
            {
                periods[i].data.label=parentEventLabel+'.'+(index+1).toString();
            }
        }
    });
}

/**
 * Get maximum event idx
 * @return {Number}
 */
function getMaxEventIdx()
{
    var maxIdx=-1;
    $(document.getElementById('behavioral_events')).children("[id^=behavioral_event]").each(function(index){
        var eventIdx=parseInt(this.getElementsByClassName('behavioral_event-idx')[0].textContent);
        if(eventIdx>maxIdx)
            maxIdx=eventIdx;
    });
    return maxIdx;
}

/**
 * Get maximum subevent index for given event
 * @param eventIdx - event index
 * @return {Number}
 */
function getMaxSubeventIdx(eventIdx)
{
    var maxIdx=-1;
    $(document.getElementById('sub_behavioral_events_list-'+eventIdx)).children("[id^=sub_behavioral_event]").each(function(index){
        var subeventIdx=parseInt(this.getElementsByClassName('sub_behavioral_event-idx')[0].textContent);
        if(subeventIdx>maxIdx)
            maxIdx=subeventIdx;
    });
    return maxIdx;
}

function updateParentEventField(parentIdx, fieldName, subEventValue)
{
    var parentValues=document.getElementById('behavioral_event-'+parentIdx+'-'+fieldName).textContent.split(', ');
    var subEventValues=subEventValue.split(', ');
    for(var i=0; i<subEventValues.length; i++)
    {
        // Look for subevent context in parent event
        var found=false;
        for(var j=0; j<parentValues.length; j++)
        {
            if(subEventValues[i]==parentValues[j])
            {
                found=true;
                break;
            }
        }
        // If not found, add to parent contexts
        if(!found)
        {
            parentValues.push(subEventValues[i]);
        }
    }
    // Update parent contexts
    var valueString='';
    if(parentValues.length>1)
        valueString=parentValues.join(', ');
    else if(parentValues.length>0)
        valueString=parentValues[0];
    document.getElementById('behavioral_event-'+parentIdx+'-'+fieldName).textContent=valueString;
}

function insertSubEvent(parentEventIdx, data)
{
    // Get template for subevent
    var tmplMarkup = $('#behavioral_subevent-template').html();
    // Fill in template
    var compiledTmpl = _.template(tmplMarkup, data);

    var count = $(document.getElementById('sub_behavioral_events_list-'+parentEventIdx)).children("[id^=sub_behavioral_event]").length;
    // No other subevents - add to end of parent event subevent list
    if(count==0)
        $(document.getElementById('sub_behavioral_events_list-'+parentEventIdx)).append(compiledTmpl);
    // Figure out where to insert subevent
    else
    {
        // Iterate through subevents of parent Event
        $(document.getElementById('sub_behavioral_events_list-'+parentEventIdx)).children("[id^=sub_behavioral_event]").each(function(index){
            // Insert before current subevent
            var thisElemStart=parseFloat(this.getElementsByClassName('sub_behavioral_event-start_time')[0].textContent);
            if(data.start_time<thisElemStart)
            {
                $(this).before(compiledTmpl);
                return false;
            }
            // Add after only subevent
            else if(index==(count-1))
            {
                $(document.getElementById('sub_behavioral_events_list-'+parentEventIdx)).append(compiledTmpl);
                return false;
            }
            else
            {
                // Insert between this subevent and the next
                var nextElemStart=parseFloat($(document.getElementById('sub_behavioral_events_list-'+parentEventIdx)).children("[id^=sub_behavioral_event]")[index+1].getElementsByClassName('sub_behavioral_event-start_time')[0].textContent);
                if(data.start_time>=thisElemStart && data.start_time<=nextElemStart)
                {
                    $(this).after(compiledTmpl);
                    return false;
                }
            }
        });
    }
}

function insertEvent(data)
{
    // Get template for subevent
    var tmplMarkup = $('#behavioral_event-template').html();
    // Fill in template
    var compiledTmpl = _.template(tmplMarkup, data);

    // Number of other events in observation session
    var count = $('#behavioral_events').children("[id^=behavioral_event]").length;

    // No other events - add to end of ob session event list
    if(count==0)
        $('#behavioral_events').append(compiledTmpl);
    // Figure out where to insert event
    else
    {
        // Iterate through each event
        $('#behavioral_events').children("[id^=behavioral_event]").each(function(index)
        {
            // Insert after this event
            var thisElemStart=parseFloat(this.getElementsByClassName('behavioral_event-start_time')[0].textContent);
            if(data.start_time<thisElemStart)
            {
                $(this).before(compiledTmpl);
                return false;
            }
            // Add after only subevent
            else if(index==(count-1))
            {
                $(document.getElementById('behavioral_events')).append(compiledTmpl);
                return false;
            }
            else
            {
                // Insert between this subevent and the next
                var nextElemStart=parseFloat($('#behavioral_events').children("[id^=behavioral_event]")[index+1].getElementsByClassName('behavioral_event-start_time')[0].textContent);
                if(data.start_time>=thisElemStart && data.start_time<=nextElemStart)
                {
                    $(this).after(compiledTmpl);
                    return false;
                }
            }
        });
    }
}
