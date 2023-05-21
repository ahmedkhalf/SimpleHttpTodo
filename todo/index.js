var task_list = document.getElementById('task-list');
var task_template = document.getElementById('task-template');
var form = document.getElementById('todo-form');
form.onsubmit = function(event){
  event.preventDefault();

  var xhr = new XMLHttpRequest();
  var formData = new FormData(form);

  // open the request
  // TODO remove hardcoded url
  xhr.open('POST', 'http://localhost/add')
  xhr.setRequestHeader("Content-Type", "application/json");

  // send the form data
  xhr.send(JSON.stringify(Object.fromEntries(formData)));

  xhr.onreadystatechange = function() {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      form.reset(); // reset form after AJAX success
      const task = task_template.cloneNode(false);
      task.id = '';
      task.className = '';
      task.innerText = formData.get("item-content");
      task_list.prepend(task);
    }
  }

  // Fail the onsubmit to avoid page refresh.
  return false; 
}
