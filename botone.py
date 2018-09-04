import os;
import re;

import time;

from slackclient import SlackClient;
from random import randint;

import commands;
import schedule;

# Instantiate the client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'));

botone_id = None;
todo_list = list();
topp_todo_list = list();

active_todo = 'No active todo found';

RTM_READ_DELAY = 1;

# Commands
EXAMPLE_COMMAND = "excmd";
SET_ACTIVE_TODO_COMMAND = "set active todo";
SET_TODO_COMMAND = "set todo";
READ_ALL_TODO_COMMAND = "what to do";
READ_ACTIVE_TODO_COMMAND = "what am i doing";
DONE_COMMAND = "done";
NEW_TODO_COMMAND = "new todo";

# REGEX
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# Filename
TODOFILENAME = 'todo.txt';
DONEFILENAME = 'done.txt';

# Misc Globals
MAX_IMAGE_ID_NO = 9999999999;

#ACTIVE_CHANNEL = os.environ.get('PROD_CHAN');
ACTIVE_CHANNEL = os.environ.get('QA_CHAN');


# Define remiders
# Refactor this
def sched_reminder(message, img_tag, img_title):
        channel = ACTIVE_CHANNEL;
        default_response = "Undefined reminder";
        if message:
                response = message;
        
        print("sched_reminder invoked!");

def parse_human_message(message, user):
        print("its a human message: " + message);
        print("message is from: " + user);

        
def parse_bot_commands(slack_events):
	"""
		Parases a list of commands
		If command if found returns a tuple of command and channel
		else returns None, None
	"""
	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"]);
			if user_id == botone_id:
				return message, event["channel"];
                        elif event['user'] != botone_id:
                                parse_human_message(event["text"], event["user"]);
	return None, None;

def parse_direct_mention(message_text):
	"""
		Finds a direct mention
		Returns user ID which was mentioned 
		Else returns None
	"""
	matches = re.search(MENTION_REGEX, message_text);
	return(matches.group(1), matches.group(2).strip()) if matches else (None, None);

def handle_command(command, channel):
	"""
		Execute a command. Idiot.
	"""
        global active_todo;
        global todo_list;
        global topp_todo_list;
        
	default_response  = "Not a valid command.";

	# Find and exec the command
	response = None;
	if command.startswith(EXAMPLE_COMMAND):
		response = "AAAAAAAAAAAAAAAAAA";
        elif command.startswith(DONE_COMMAND):
                filename = DONEFILENAME;
                if(active_todo != None):
                        response = 'Task complete. Good job!';
                        with open(filename, 'a') as done_file:
                                fstr = "%a, %d %b %Y %H:%M:%S";
                                gmt = time.localtime();
                                time_str = time.strftime(fstr, gmt);
                                done_file.write(time_str + ' ' + \
                                                active_todo + '\n'
                                );
                                done_file.close();
                        active_todo = None;
                else:
                        response = 'Hmm... There is no active task';
        elif command.startswith(SET_TODO_COMMAND):
                response = "I changed priority for you.";
                todo_choice = command;
                todo_choice = todo_choice.replace(
                        SET_TODO_COMMAND, '', 1
                );
                todo_choice = todo_choice.strip();
                item_code, target_type = todo_choice.split(' ', 1);
                print('todo choice: ' + todo_choice);
                print('item code: ' + item_code);
                print('target_type: ' + target_type);

                if(target_type == 'active' and active_todo != None):
                        response = "Theres already an active todo: " \
                                   + active_todo;
                elif(item_code[:1] == 'n'):
                        set_todo(item_code[:1], item_code[1:], \
                                 target_type);
                elif(item_code[:1] == 't'):
                        set_todo(item_code[:1], item_code[1:], \
                                 target_type);
                elif(item_code[:1] == 'a'):
                        set_todo(item_code[:1], 0, target_type);
                else:
                        response = "invalid item code";
        elif command.startswith(SET_ACTIVE_TODO_COMMAND):
                response = "Invoking set active todo command";
                
                todo_choice = command;
                todo_choice = todo_choice.replace(
                        SET_ACTIVE_TODO_COMMAND, '', 1
                );
                todo_choice = todo_choice.strip();
                
                print(todo_choice);

                if(not todo_choice.isdigit() or
                   int(todo_choice) > len(todo_list)-1):
                        response = "Not a valid choice";
                elif(active_todo == None):
                        active_todo = todo_choice;
                        response = "Active todo: " + \
                                   active_todo;
                else:
                        response = "An active todo already exists: " \
                                   + active_todo;
        elif command.startswith(READ_ALL_TODO_COMMAND):
                # Set response to empty string so we can
                # append stuff to it
                response = "";
                
                if(count_todo() <= 0):
                        response = "No todos.... Something is wrong";
                
                for index, todo_item in enumerate(todo_list):
                        response = response + '>n' + str(index) \
                                   + '. ' + todo_item + '\n';
                        
                if(len(topp_todo_list) > 0):
                        response = response + \
                                   'These items are high ' + \
                                   'priority:' + '\n';
                for index, todo_item in enumerate(topp_todo_list):
                        response = response + '>t' + \
                                   str(index) + '. ' + \
                                   todo_item + '\n';

                if(active_todo != None):
                        response = response + \
                                   "Currently you're supposed " + \
                                   "to be working on:" + '\n';
                        response = response + '>a. ' + \
                                   active_todo + '\n';
        elif command.startswith(READ_ACTIVE_TODO_COMMAND):
                response = read_active_todo();
        elif command.startswith(NEW_TODO_COMMAND):
                response = "Todo item added";
                new_todo = command.replace(
                        NEW_TODO_COMMAND, '', 1
                );
                new_todo = new_todo.strip();
                if(len(new_todo) > 1):
                        todo_list.append(new_todo);
                        save_todo();
                else:
                        response = "Empty todo item?";
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response or default_response
	);

def count_todo():
        return str(len(todo_list) + len(topp_todo_list) + 1);

# def read_all_todo():

def read_active_todo():
        response = "Nothing set to active";
        if (active_todo == None):
                return response;

        response = "You should be working on: " + active_todo + "\n";

        if(len(topp_todo_list) > 0):
                response = response + "The task on deck is: ";
                response = response + topp_todo_list[0] + '\n';
        elif(len(todo_list) > 0):
                response = response + "The task on deck is: ";
                response = response + topp_list[0] + '\n';

        return response;

def set_todo(item_type, item_index, target_type):
        global todo_list;
        global topp_todo_list;
        global active_todo;

        print('set_todo invoked...');
        print('item_type: ' + item_type);
        print('item_index: ' + str(item_index));
        print('target_type: ' + target_type);
        print('todo_list len: ' + str(len(todo_list)));

        item = "Invalid item definintion";
        
        if item_type == 'n' and int(item_index) < len(todo_list):
                item = todo_list[int(item_index)];
                del todo_list[int(item_index)];
                print('setting a normal priority todo ' \
                      + item);
                # todo_list.append(item);
        elif item_type == 't' and int(item_index) < len(topp_todo_list):
                item = topp_todo_list[int(item_index)];
                del topp_todo_list[int(item_index)];
                print('setting a top priority todo ' \
                      + item);
                # topp_todo_list.append(item);
        elif item_type == 'a' and active_todo != None:
                print('setting the active todo ' \
                      + active_todo);
                item = active_todo;
                active_todo = None;
        else:
                print("Invalid item code");
                return;
        if(target_type == 'normal'):
                todo_list.append(item);
                save_todo();
        elif(target_type == 'urgent'):
                topp_todo_list.append(item);
                save_todo();
        elif(target_type == 'active' and active_todo == None):
                active_todo = item;
                save_todo();

# def save_todo(item_type, item):
#         global todo_list;
#         global topp_todo_list;
#         global active_todo;
        
#         filename = TODOFILENAME;
        
#         if item_type == 'n':
#                 todo_list.append(item);
#         elif item_type == 't':
#                 topp_todo_list.append(item);
#         elif item_type == 'a':
#                 active_todo = item;

#         # Save to the file
#         with open(filename, 'a') as todo_file:
#                 todo_file.write(item_type + '||' + item + '\n');
#                 todo_file.close();
                
def save_todo():
        filename = TODOFILENAME;

        print('Invoking save_todo');

        with open(filename, 'w') as todo_file:
                for todo_item in todo_list:
                        todo_file.write(
                                'n' + '||' + todo_item + '\n'
                        );
                for todo_item in topp_todo_list:
                        todo_file.write(
                                't' + '||' + todo_item + '\n'
                        );
                if active_todo != None:
                        todo_file.write(
                                'a' + '||' + active_todo + '\n'
                        );
                todo_file.close();

def load_todo():
        filename = TODOFILENAME;
        global todo_list;
        global topp_todo_list;
        global active_todo;
        
        print("loading todo list");
        with open(filename, 'r') as todo_file:
                todo_list = [l.rstrip('\n') for l in todo_file];
                todo_file.close();

        # Go thrugh the list backwards so we can remove stuff from the list
        i = (len(todo_list) - 1);
        while (i >= 0):
                item_type, item = todo_list[i].split('||', 1);
                if item_type == 'n':
                        todo_list[i] = item;
                elif item_type == 'a':
                        active_todo = item;
                        del todo_list[i];
                elif item_type == 't':
                        topp_todo_list.append(item);
                        del todo_list[i];
                # Decrement the list
                i -=1;
        print("loaded " + count_todo()  + " tasks");

# Schedule stuff
#schedule.every(1).minute.do();
if __name__ == "__main__":
	if slack_client.rtm_connect(with_team_state=False):
                # Pre loop stuff

                # Sexy intro
                load_todo();
		print("botone waking up...");
                
		# Read ID
		botone_id = slack_client.api_call("auth.test")["user_id"];
                
		while True:
                        schedule.run_pending();
			command, channel = parse_bot_commands(slack_client.rtm_read());
			if command:
				handle_command(command, channel);
			time.sleep(RTM_READ_DELAY);
	else:
		print("CONNECTION FAILED!!!!!");
