def print_pax_info(bot, update, user_data):
    for pax in user_data['paxes']:
        update.message.reply_text("{}({})".format(pax['name'], pax['age']))


def set_name_to_current_pax(user_data, text):
    if "paxes" not in user_data.keys():
        user_data["paxes"] = [{}]
    user_data['paxes'][len(user_data['paxes'])-1]["name"] = text


def set_age_to_current_pax(user_data, text):
    user_data['paxes'][len(user_data['paxes']) - 1]["age"] = text


def add_pax(user_data):
    user_data['paxes'].append({})


def reset_paxes(user_data):
    user_data['paxes'] = [{}]
