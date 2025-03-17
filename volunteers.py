from flask import Flask, render_template, request, redirect, url_for, Blueprint
from fetch_volunteer_data import *
from fetch_data import *
from decorators import *
from functions import *

volunteers_bp = Blueprint('volunteers', __name__)

@volunteers_bp.route('/admin_manage_events', methods=['GET', 'POST'])
@admin_login_required
def event_manager():
    if request.method == 'POST':
        try:
            print(dict(request.form))
            form_data = dict(request.form)
            
            # Track newly created IDs to map temporary IDs to real database IDs
            new_id_mapping = {}
            
            # Get all existing data to compare with form data
            all_events = get_all_events_nested()
            
            # Track which items are present in the current form submission
            present_events = set()
            present_roles = set()
            present_positions = set()
            
            # STAGE 1: Process all events first
            for key, value in form_data.items():
                if not key.startswith('event--'):
                    continue
                
                parts = key.split('--')
                if len(parts) < 2:
                    continue
                
                # Skip empty fields
                value = value.strip()
                if not value:
                    continue
                
                if parts[1].startswith('new-event'):
                    # Add new event
                    new_event_id = add_event(value)
                    # Store mapping from temporary ID to real DB ID
                    new_id_mapping[parts[1]] = new_event_id
                    present_events.add(new_event_id)
                else:
                    # Update existing event
                    event_id = int(parts[1])
                    update_event(event_id, value)
                    present_events.add(event_id)
            
            # STAGE 2: Process all roles
            for key, value in form_data.items():
                if not key.startswith('role--'):
                    continue
                
                parts = key.split('--')
                if len(parts) < 3:
                    continue
                
                # Skip empty fields
                value = value.strip()
                if not value:
                    continue
                
                # Get the event ID, checking if it's a newly created event
                event_id = parts[1]
                if event_id in new_id_mapping:
                    event_id = new_id_mapping[event_id]
                else:
                    event_id = int(event_id)
                
                if parts[2].startswith('new-role'):
                    # Add new role
                    new_role_id = add_role(event_id, value)
                    # Store mapping from temporary ID to real DB ID
                    temp_role_id = parts[2]
                    new_id_mapping[f"{event_id}--{temp_role_id}"] = new_role_id
                    present_roles.add(new_role_id)
                else:
                    # Update existing role
                    role_id = int(parts[2])
                    update_role(role_id, value)
                    present_roles.add(role_id)
            
            # STAGE 3: Process all positions
            for key, value in form_data.items():
                if not key.startswith('position--'):
                    continue
                
                parts = key.split('--')
                if len(parts) < 4:
                    continue
                
                # Skip empty fields
                value = value.strip()
                if not value:
                    continue
                
                # Get the event ID, checking if it's a newly created event
                event_id = parts[1]
                if event_id in new_id_mapping:
                    event_id = new_id_mapping[event_id]
                else:
                    event_id = int(event_id)
                
                # Get the role ID, checking if it's a newly created role
                temp_role_id = parts[2]
                role_id = temp_role_id
                
                # Check if this is a reference to a newly created role
                role_mapping_key = f"{event_id}--{temp_role_id}"
                if role_mapping_key in new_id_mapping:
                    role_id = new_id_mapping[role_mapping_key]
                else:
                    role_id = int(role_id)
                
                if parts[3].startswith('new-position'):
                    # Add new position
                    new_position_id = add_position(role_id, value)
                    present_positions.add(new_position_id)
                else:
                    # Update existing position
                    position_id = int(parts[3])
                    update_position(position_id, value)
                    present_positions.add(position_id)
            
            # STAGE 4: Delete items that are no longer present in the form
            
            # First, collect all existing IDs from the database
            existing_events = set()
            existing_roles = set()
            existing_positions = set()
            
            for event in all_events:
                event_id = event['event_id']
                existing_events.add(event_id)
                
                for role in event['roles']:
                    role_id = role['role_id']
                    existing_roles.add(role_id)
                    
                    for position in role['positions']:
                        position_id = position['position_id']
                        existing_positions.add(position_id)
            
            # Delete positions first (child items)
            positions_to_delete = existing_positions - present_positions
            for position_id in positions_to_delete:
                delete_position(position_id)
            
            # Delete roles next
            roles_to_delete = existing_roles - present_roles
            for role_id in roles_to_delete:
                delete_role(role_id)
            
            # Delete events last (parent items)
            events_to_delete = existing_events - present_events
            for event_id in events_to_delete:
                delete_event(event_id)
            
            return redirect(url_for('volunteers.event_manager'))
            
        except Exception as e:
            # Log the error
            print(f"Error in event manager: {str(e)}")
            # In a real app, you'd want to flash a message or log properly
            return redirect(url_for('volunteers.event_manager'))
            
    elif request.method == "GET":
        position_options = get_all_volunteering_parent_names()
        # GET: render the admin page with existing events, roles, positions, and predefined options.
        return render_template_with_session('admin_event_management.html', 
                              events=get_all_events_nested(), 
                              position_options=position_options)

@volunteers_bp.route('/volunteer_management', methods=['GET', 'POST'])
@login_required
def volunteer_management():
    if request.method == "GET":
        print(get_all_events_nested())
        return render_template_with_session('volunteering.html', events=get_all_events_nested())
    elif request.method == "POST":
        print(request.form)
        #request.form.get("")

