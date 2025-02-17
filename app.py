from flask import Flask, render_template, request, redirect, url_for
import fetch_data

app = Flask(__name__)

# At startup, make sure our database tables exist.
fetch_data.create_events_table()
fetch_data.create_roles_table()
fetch_data.create_positions_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        print(dict(request.form))
        # Process form data.
        # (This example uses a simple naming scheme for inputs.
        # For a real dynamic nested form you might want to use JavaScript
        # to build a JSON payload or use field names that let you parse the data more easily.)
        #
        # We assume input names are formatted as:
        #    event--<id>          for updating an existing event,
        #    event--new-event-<#>  for a new event,
        #    role--<event_id>--<id> for updating an existing role,
        #    role--<event_id>--new-role-<#>  for a new role,
        #    position--<event_id>--<role_id>--<id> for updating a position, or
        #    position--<event_id>--<role_id>--new-position-<#>  for a new position.
        #
        # Here we simply loop over the keys.
        form_data = dict(request.form)
        # Loop through each key/value pair in the POST data.
        for key, value in form_data.items():
            print(f"Key: {key}, Value: {value}")
            parts = key.split('--')
            if parts[0] == 'event':
                # parts[1] is either an existing ID or a new event identifier.
                if parts[1].startswith('new-event'):
                    if value.strip() != "":
                        fetch_data.add_event(value.strip())
                else:
                    event_id = parts[1]
                    fetch_data.update_event(event_id, value.strip())
            elif parts[0] == 'role':
                # parts[1] = event_id, parts[2] = role id (or new role identifier)
                if parts[2].startswith('new-role'):
                    if value.strip() != "":
                        event_id = parts[1]
                        fetch_data.add_role(event_id, value.strip())
                else:
                    role_id = parts[2]
                    fetch_data.update_role(role_id, value.strip())
            elif parts[0] == 'position':
                # parts[1] = event_id, parts[2] = role_id, parts[3] = position id (or new position identifier)
                if parts[3].startswith('new-position'):
                    if value.strip() != "":
                        role_id = parts[2]
                        fetch_data.add_position(role_id, value.strip())
                else:
                    position_id = parts[3]
                    fetch_data.update_position(position_id, value.strip())
        return redirect(url_for('admin'))
    elif request.method == "GET":
        # GET: render the admin page with existing events, roles, positions, and predefined options.
        return render_template('admin.html', events=fetch_data.get_all_events_nested(), predefined_position_options=["Volunteer A", "Volunteer B", "Volunteer C"])


@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    if request.method == 'POST':
        # Process volunteer selections.
        # We expect form keys like "volunteer--<position_id>"
        for key, value in request.form.items():
            if key.startswith('volunteer--'):
                position_id = key.split('--')[1]
                # Here we update the position with the volunteer’s account name.
                # (In a full application you would validate that the user is allowed to volunteer, etc.)
                fetch_data.update_position_volunteer(position_id, value.strip())
        return redirect(url_for('volunteer'))
    # GET: load the current events (with nested roles and positions)
    events = fetch_data.get_all_events_nested()
    return render_template('volunteer.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)
