// Constants to declare weekdays and months
const WEEKDAYS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]; 
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

// Global Variables
var date = 0; // Date is declared initially to allow for flag to show date is not set

function start_time() {
  /*
  Function to start the time count. Designed to recurse every second, and retrieve date each time. 
  The date is then restructured to a displayable string and passed to the time html ID object.
  */
  
  let today = new Date(); 
  let hours = today.getHours(); 
  let minutes = today.getMinutes(); 
  let seconds = today.getSeconds(); 

  getDate(today);

  hours = checkTime(hours); 
  minutes = checkTime(minutes); 
  seconds = checkTime(seconds); 
  document.getElementById('time').innerHTML =  hours + ":" + minutes + ":" + seconds;
  setTimeout(start_time, 1000); 
}

function checkTime(value) {
  /*
  Function to format any values in time to have 0 in front of, if needed
  Takes value as parameter and returns once formatted
  */
  if (value < 10) {value = "0" + value}; 
  return value; 
}

function getDate(today){
  /*
  Function to get date. Retrieves date value, formats for view and updates html
  If statement finds if date needs to updated
  Passes to date id
  */ 
  if (date != today.getDate()) { 
    let day = WEEKDAYS[today.getDay()]; 
    date = today.getDate(); 
    let month = MONTHS[today.getMonth()]; 
    let year = today.getFullYear(); 
    document.getElementById('date').innerHTML =`${day} ${date}<sup id="ordinal-suffix">${getOrdinalSuffix(date)}</sup> ${month}, ${year}`; 
  }
}

function getOrdinalSuffix(date){
  /*
  Uses date number to find what suffix is needed based on some basic rules
  Any number that is 1,2 or 3 uses the standard suffix
  Else, th
  */
  if (date > 3 && date < 21) return 'th'; 
  switch (date % 10) {
    case 1:  return "st";
    case 2:  return "nd";
    case 3:  return "rd";
    default: return "th";
  }
}

start_time();
