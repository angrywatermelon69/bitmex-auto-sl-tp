import settings
import os
import time
from api import BitmexApi
from threading import Thread
from utils import stop_bot

settings_mode = False
config = {}

# TODO: use CONSTANTS to hold string values

def user_input():
    global settings_mode
    while True:
        print('\nType "start" to run the bot, or "settings" to change settings. Type "help" to see available commands.')
        if settings_mode:
            time.sleep(1)
            continue
        command = input().strip().lower()
        if command == 'quit':
            stop_bot()
        elif command == 'help':
            str_help = ('\n----------HELP----------\n\n'
                        'quit -- shut down the bot\n'
                        'settings -- change settings\n'
                        'info -- show all account info')
            print(str_help)
        elif command == 'settings':
            print('\n Settings mode enabled. Type "cancel" to go back.\n')
            settings_mode = True
            settings_edit()
        # TODO: handle info display
        elif command != '':
            print('Invalid command entered!')

def input_hook(valid_opts):
    str_opts = ''
    for x in valid_opts:
        str_opts += '\n%s' %(x)
    str_opts += '\ncancel'
    while True:
        inp = input().strip().lower()
        if inp == 'cancel':
            return None
        elif inp == 'help':
            print('Choose one of the following: %s' %(str_opts))
        elif type(valid_opts) is list:
            # handle list options
            for y in valid_opts:
                if y in inp or inp == y:
                    return inp
            print('Invalid option! Choose one of the following: %s' %(str_opts))
        elif type(valid_opts) is dict:
            # handle dictionary options
            for k in valid_opts.keys():
                if k in inp:
                    _value = inp.replace(k,'').strip()
                    try: 
                        if k in ['api key', 'api secret']:
                            valid_opts[k] = _value
                        else:
                            float(_value)
                            valid_opts[k] = _value
                        return valid_opts
                    except:
                        break
            print('Invalid option! Choose one of the following: %s' %(str_opts))

def settings_edit():
    global settings_mode, config
    # list accounts
    accounts = config['accounts']
    max_acc = len(accounts)

    # display accounts
    i = 0
    str_display = ''
    for a in accounts:
        str_display += '\nAcc: %s\nAPI KEY: %s\nAPI SECRET: %s\n'\
                        %(i, a['api']['key'], a['api']['secret'])
        i += 1
    print(str_display)

    # wait for valid input (existing acc no) TODO: add new account
    print('Type in account number, e.g. "0" or "new" to add a new one')
    current_accs = []
    for a in range(0, max_acc):
        current_accs.append(str(a))
    current_accs.append('new')
    inp_acc = input_hook(current_accs)

    # handle cancel command
    if inp_acc == None:
        settings_mode = False
        print('Settings mode disabled.\n')
        return
    
    # handle new acc
    if inp_acc == 'new':
        new_acc = {
            'api': {'key': '', 'secret': ''},
            'sl': {'dist': 0.02, 'trail': 0.005},
            'tp': {'dist': 0.05}
        }
        accounts.append(new_acc)
        config['accounts'] = accounts
        print('New account added.')
        settings.save_settings(config)
        settings_mode = False
        print('Settings mode disabled.\n')
        return
    # show account settings
    acc = int(inp_acc)
    _acc = accounts[int(inp_acc)]
    str_display = 'SELECTED ACC: %s\nAPI KEY: %s\nAPI SECRET: %s\n'\
                        %(acc, _acc['api']['key'], _acc['api']['secret'])
    # add SL/TP settings to display
    sl_dist = str(_acc['sl']['dist'] * 100) + '%'
    sl_trail = str(_acc['sl']['trail'] * 100) + '%'
    tp_dist = str(_acc['tp']['dist'] * 100) + '%'
    str_display += 'SL Distance: %s\nSL Trail: %s\nTP Distance: %s\n'\
                        %(sl_dist, sl_trail, tp_dist)
    print(str_display)

    # choose setting to change
    while True:
        print('\nType "sl distance 1" to set a stop loss distance of 1%. Or type "help" for a list of available commands.')
        _modif = input_hook(
            {
                'sl distance': '',
                'sl trail': '',
                'tp distance': '',
                'api key': '',
                'api secret': ''
            }
        )
        if _modif == None:
            break
        if _modif['sl distance'] is not '':
            # change SL Distance
            _value = float(_modif['sl distance'])
            config['accounts'][acc]['sl']['dist'] = _value / 100
        elif _modif['sl trail'] is not '':
            # change SL Trail
            _value = float(_modif['sl trail'])
            config['accounts'][acc]['sl']['trail'] = _value / 100
        elif _modif['tp distance'] is not '':
            # change TP Distance
            _value = float(_modif['tp distance'])
            config['accounts'][acc]['tp']['dist'] = _value / 100
        elif _modif['api key'] is not '':
            # change api key
            _value = str(_modif['api key']).strip()
            config['accounts'][acc]['api']['key'] = _value
        elif _modif['api secret'] is not '':
            # change api secret
            _value = str(_modif['api secret']).strip()
            config['accounts'][acc]['api']['secret'] = _value
        # save settings prompt
        while True:
            save = input('Save changes? Y/N').lower().strip()
            if save == 'y':
                settings.save_settings(config)
                break
            elif save == 'n':
                config = settings.get_settings() # reload settings
                print('No changes were saved.')
                break
            
    settings_mode = False
    print('Settings mode disabled.\n')

if __name__ == '__main__':
    print('BitMEX Auto Stop Loss and Take Profit Bot')
    print('Loading settings...',end='')
    settings._init()
    config = settings.get_settings()
    print('done\n')
    # init CLI mode
    Thread(target=user_input).start()
    

    